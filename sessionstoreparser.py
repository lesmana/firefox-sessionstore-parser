#! /usr/bin/env python

import getopt
import json

class Error(Exception):
  pass

class ArgvParser(object):
  def __init__(self, getoptfunc, optionsdata, argumentsdata):
    self.getoptfunc = getoptfunc
    self.optionsdata = optionsdata
    self.argumentsdata = argumentsdata

  def splitprogname(self, argv):
    progname = argv[0]
    argvoptsargs = argv[1:]
    return progname, argvoptsargs

  def prepareoptstring(self, opt, argcount, argmod):
    strippedopt = opt.lstrip('-')
    if argcount == 0:
      optstring = strippedopt
    else:
      optstring = strippedopt + argmod
    return optstring

  def prepareopt(self, opt, argcount):
    shortoptslist = []
    longopts = []
    if opt.startswith('--'):
      optstring = self.prepareoptstring(opt, argcount, '=')
      longopts.append(optstring)
    else:
      optstring = self.prepareoptstring(opt, argcount, ':')
      shortoptslist.append(optstring)
    return shortoptslist, longopts

  def prepareoptiondata(self, optiondata):
    shortoptslist = []
    longopts = []
    optnames = {}
    name, opts, argcount = optiondata
    for opt in opts:
      shorts, longs = self.prepareopt(opt, argcount)
      shortoptslist.extend(shorts)
      longopts.extend(longs)
      optnames[opt] = name
    return shortoptslist, longopts, optnames

  def prepareoptionsdata(self, optionsdata):
    # no error checking
    # let's assume everyone is sane
    shortoptslist = []
    longopts = []
    optnames = {}
    for optiondata in optionsdata:
      shorts, longs, names = self.prepareoptiondata(optiondata)
      shortoptslist.extend(shorts)
      longopts.extend(longs)
      optnames.update(names)
    shortopts = ''.join(shortoptslist)
    return shortopts, longopts, optnames

  def dictifyopts(self, opts, optnames):
    optsdict = {}
    for opt, val in opts:
      name = optnames[opt]
      optsdict[name] = val
    return optsdict

  def splitopts(self, argvoptsargs):
    shortopts, longopts, optnames = self.prepareoptionsdata(self.optionsdata)
    opts, argvargs = self.getoptfunc(argvoptsargs, shortopts, longopts)
    optsdict = self.dictifyopts(opts, optnames)
    return optsdict, argvargs

  def splitargs(self, argvargs):
    argsdict = {}
    argvrest = argvargs
    for name in self.argumentsdata:
      if len(argvrest) > 0:
        arg = argvrest[0]
        argvrest = argvrest[1:]
        argsdict[name] = arg
      else:
        break
    return argsdict, argvrest

  def combine(self, progname, optsdict, argsdict, argvrest):
    parsedargv = {}
    parsedargv['progname'] = progname
    parsedargv.update(optsdict)
    parsedargv.update(argsdict)
    if len(argvrest) > 0:
      parsedargv['unknown'] = argvrest
    return parsedargv

  def tryparse(self, argv):
    progname, argvoptsargs = self.splitprogname(argv)
    optsdict, argvargs = self.splitopts(argvoptsargs)
    argsdict, argvrest = self.splitargs(argvargs)
    parsedargv = self.combine(progname, optsdict, argsdict, argvrest)
    return parsedargv

  def parse(self, argv):
    try:
      parsedargv = self.tryparse(argv)
      return parsedargv
    except getopt.GetoptError as err:
      unknownoption = str(err).split()[1]
      parsedargv = {'unknown': [unknownoption]}
      return parsedargv

class JsonReaderError(Error):
  pass

class JsonReader(object):
  def __init__(self, openfunc, jsonloadfunc):
    self.openfunc = openfunc
    self.jsonloadfunc = jsonloadfunc

  def openfile(self, filename):
    try:
      fileob = self.openfunc(filename)
      return fileob
    except IOError:
      raise JsonReaderError('error: cannot open file %s.' % filename)

  def jsonload(self, fileob, filename):
    try:
      sessionstore = self.jsonloadfunc(fileob)
      return sessionstore
    except ValueError:
      raise JsonReaderError(
            'error: cannot read session store from file %s.' % filename)

  def read(self, filename):
    with self.openfile(filename) as fileob:
      sessionstore = self.jsonload(fileob, filename)
    return sessionstore

class OpenUrlGenerator(object):
  def __init__(self):
    pass

  def handleurl(self, tab):
    openindex = tab['index'] - 1
    openentry = tab['entries'][openindex]
    openurl = openentry['url']
    yield openurl

  def handlewindow(self, window):
    for tab in window['tabs']:
      for url in self.handleurl(tab):
        yield url

  def handlesessionstore(self, sessionstore):
    for window in sessionstore['windows']:
      for url in self.handlewindow(window):
        yield url

  def generate(self, sessionstore):
    for plainurl in self.handlesessionstore(sessionstore):
      url = {'url': plainurl}
      yield url

class UrlWriter(object):
  def __init__(self, stdout):
    self.stdout = stdout

  def write(self, urls):
    for url in urls:
      self.stdout.write(url['url'] + '\n')

class SessionStoreParser(object):
  def __init__(self, jsonreader, urlgenerator, urlwriter):
    self.jsonreader = jsonreader
    self.urlgenerator = urlgenerator
    self.urlwriter = urlwriter

  def getsessionstore(self, filename):
    sessionstore = self.jsonreader.read(filename)
    return sessionstore

  def geturls(self, sessionstore):
    urls = self.urlgenerator.generate(sessionstore)
    return urls

  def writeurls(self, urls):
    self.urlwriter.write(urls)

  def parse(self, filename):
    sessionstore = self.getsessionstore(filename)
    urls = self.geturls(sessionstore)
    self.writeurls(urls)

class SessionStoreParserWorker(object):
  def __init__(self, sessionstoreparser, filename):
    self.sessionstoreparser = sessionstoreparser
    self.filename = filename

  def __call__(self):
    self.sessionstoreparser.parse(self.filename)
    return 0

class HelpWriterWorker(object):
  def __init__(self, stream, message, exitstatus):
    self.stream = stream
    self.message = message
    self.exitstatus = exitstatus

  def __call__(self):
    self.stream.write(self.message + '\n')
    return self.exitstatus

class WorkerFactory(object):
  def __init__(self, sessionstoreparser, sessionstoreparserworkerclass, stderr):
    self.sessionstoreparser = sessionstoreparser
    self.sessionstoreparserworkerclass = sessionstoreparserworkerclass
    self.stderr = stderr

  def produce(self, parsedargv):
    if 'unknown' in parsedargv:
      exitstatus = 2
      unknownoption = parsedargv['unknown'][0]
      message = 'unknown option: %s' % (unknownoption)
      worker = HelpWriterWorker(self.stderr, message, exitstatus)
    elif 'filename' not in parsedargv:
      exitstatus = 2
      message = 'missing argument: filename'
      worker = HelpWriterWorker(self.stderr, message, exitstatus)
    else:
      filename = parsedargv['filename']
      worker = self.sessionstoreparserworkerclass(
            self.sessionstoreparser, filename)
    return worker

class Application(object):

  def __init__(self, argvparser, workerfactory, stderr):
    self.argvparser = argvparser
    self.workerfactory = workerfactory
    self.stderr = stderr

  def parseargv(self, argv):
    parsedargv = self.argvparser.parse(argv)
    return parsedargv

  def createworker(self, parsedargv):
    worker = self.workerfactory.produce(parsedargv)
    return worker

  def dowork(self, worker):
    exitstatus = worker()
    return exitstatus

  def tryrun(self, argv):
    parsedargv = self.parseargv(argv)
    worker = self.createworker(parsedargv)
    exitstatus = self.dowork(worker)
    return exitstatus

  def run(self, argv):
    try:
      exitstatus = self.tryrun(argv)
      return exitstatus
    except Error as err:
      self.stderr.write(str(err) + '\n')
      return 1

def secludedmain(openfunc, stdout, stderr, argv):
  optionsdata = []
  argumentsdata = ['filename']
  argvparser = ArgvParser(getopt.getopt, optionsdata, argumentsdata)
  jsonreader = JsonReader(openfunc, json.load)
  urlgenerator = OpenUrlGenerator()
  urlwriter = UrlWriter(stdout)
  sessionstoreparser = SessionStoreParser(
        jsonreader, urlgenerator, urlwriter)
  workerfactory = WorkerFactory(
        sessionstoreparser, SessionStoreParserWorker, stderr)
  app = Application(argvparser, workerfactory, stderr)
  exitstatus = app.run(argv)
  return exitstatus

def main(): # pragma: no cover
  import sys
  exitstatus = secludedmain(open, sys.stdout, sys.stderr, sys.argv)
  return exitstatus
