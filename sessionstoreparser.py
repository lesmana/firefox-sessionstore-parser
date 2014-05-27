#! /usr/bin/env python

import getopt
import json

class Error(Exception):
  pass

class WindowGenerator(object):
  def __init__(self):
    pass

  def generate(self, sessionstore):
    for window in sessionstore['windows']:
      yield window

class TabGenerator(object):
  def __init__(self, windowgenerator):
    self.windowgenerator = windowgenerator

  def generate(self, sessionstore):
    for window in self.windowgenerator.generate(sessionstore):
      for tab in window['tabs']:
        yield tab

class OpenUrlGenerator(object):
  def __init__(self, tabgenerator):
    self.tabgenerator = tabgenerator

  def generate(self, sessionstore):
    for tab in self.tabgenerator.generate(sessionstore):
      openindex = tab['index'] - 1
      openentry = tab['entries'][openindex]
      openurl = openentry['url']
      yield openurl

class ArgvError(Error):
  pass

class ArgvParser(object):
  def __init__(self, getoptfunc, optionsdata):
    self.getoptfunc = getoptfunc
    self.optionsdata = optionsdata

  def splitprogname(self, argv):
    progname = argv[0]
    argvoptsargs = argv[1:]
    return progname, argvoptsargs

  def splitoptionsdata(self, optionsdata):
    # no error checking
    # let's assume everyone is sane
    shortoptslist = []
    longopts = []
    optnames = {}
    for optiondata in optionsdata:
      name, possibleopts, argcount = optiondata
      for possibleopt in possibleopts:
        if possibleopt.startswith('--'):
          # handle long opt
          strippedopt = possibleopt.lstrip('-')
          if argcount == 0:
            longopts.append(strippedopt)
          else:
            longopts.append(strippedopt + '=')
          optnames[possibleopt] = name
        else:
          # handle short opt
          strippedopt = possibleopt.lstrip('-')
          if argcount == 0:
            shortoptslist.append(strippedopt)
          else:
            shortoptslist.append(strippedopt + ':')
          optnames[possibleopt] = name
    shortopts = ''.join(shortoptslist)
    return shortopts, longopts, optnames

  def dictifyopts(self, opts, optnames):
    optsdict = {}
    for opt, val in opts:
      name = optnames[opt]
      if val == '':
        outval = True
      else:
        outval = val
      optsdict[name] = outval
    return optsdict

  def splitopts(self, argvoptsargs):
    shortopts, longopts, optnames = self.splitoptionsdata(self.optionsdata)
    opts, argvargs = self.getoptfunc(argvoptsargs, shortopts, longopts)
    optsdict = self.dictifyopts(opts, optnames)
    return optsdict, argvargs

  def splitargs(self, argvargs):
    args = argvargs
    argvunknown = []
    if len(args) != 1:
      argsdict = {}
      errormessage = 'need filename'
      argvunknown = [errormessage]
    else:
      filename = args[0]
      argsdict = {'filename': filename}
    return argsdict, argvunknown

  def combine(self, progname, optsdict, argsdict):
    options = {}
    options.update(optsdict)
    options.update(argsdict)
    return options

  def tryparse(self, argv):
    progname, argvoptsargs = self.splitprogname(argv)
    optsdict, argvargs = self.splitopts(argvoptsargs)
    argsdict, argvunknown = self.splitargs(argvargs)
    options = self.combine(progname, optsdict, argsdict)
    return options, argvunknown

  def parse(self, argv):
    try:
      options, argvunknown = self.tryparse(argv)
      return options, argvunknown
    except getopt.GetoptError as err:
      return {}, [str(err)]

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

class UrlGeneratorFactory(object):
  def __init__(self, classes):
    self.classes = classes

  def getwindowgeneratorclass(self):
    windowgeneratorclass = self.classes['windowgenerator']
    return windowgeneratorclass

  def gettabgeneratorclass(self):
    tabgeneratorclass = self.classes['tabgenerator']
    return tabgeneratorclass

  def geturlgeneratorclass(self):
    urlgeneratorclass = self.classes['urlgenerator']
    return urlgeneratorclass

  def getwindowgenerator(self):
    windowgeneratorclass = self.getwindowgeneratorclass()
    windowgenerator = windowgeneratorclass()
    return windowgenerator

  def gettabgenerator(self, windowgenerator):
    tabgeneratorclass = self.gettabgeneratorclass()
    tabgenerator = tabgeneratorclass(windowgenerator)
    return tabgenerator

  def geturlgenerator(self, tabgenerator):
    urlgeneratorclass = self.geturlgeneratorclass()
    urlgenerator = urlgeneratorclass(tabgenerator)
    return urlgenerator

  def produce(self):
    windowgenerator = self.getwindowgenerator()
    tabgenerator = self.gettabgenerator(windowgenerator)
    urlgenerator = self.geturlgenerator(tabgenerator)
    return urlgenerator

class UrlWriter(object):
  def __init__(self, stdout):
    self.stdout = stdout

  def write(self, urls):
    for url in urls:
      self.stdout.write(url + '\n')

class SessionStoreParser(object):
  def __init__(self, jsonreader, urlgeneratorfactory, urlwriter):
    self.jsonreader = jsonreader
    self.urlgeneratorfactory = urlgeneratorfactory
    self.urlwriter = urlwriter

  def getsessionstore(self, options):
    filename = options['filename']
    sessionstore = self.jsonreader.read(filename)
    return sessionstore

  def geturlgenerator(self):
    urlgenerator = self.urlgeneratorfactory.produce()
    return urlgenerator

  def geturls(self, urlgenerator, sessionstore):
    urls = urlgenerator.generate(sessionstore)
    return urls

  def writeurls(self, urls):
    self.urlwriter.write(urls)

  def parse(self, options):
    sessionstore = self.getsessionstore(options)
    urlgenerator = self.geturlgenerator()
    urls = self.geturls(urlgenerator, sessionstore)
    self.writeurls(urls)

class SessionStoreParserWorker(object):
  def __init__(self, sessionstoreparser, options):
    self.sessionstoreparser = sessionstoreparser
    self.options = options

  def __call__(self):
    self.sessionstoreparser.parse(self.options)
    return 0

class WorkerFactory(object):
  def __init__(self, sessionstoreparser, sessionstoreparserworkerclass):
    self.sessionstoreparser = sessionstoreparser
    self.sessionstoreparserworkerclass = sessionstoreparserworkerclass

  def produce(self, options, argvunknown):
    if len(argvunknown) != 0:
      raise ArgvError(argvunknown[0])
    else:
      worker = self.sessionstoreparserworkerclass(self.sessionstoreparser, options)
    return worker

class Application(object):

  def __init__(self, argvparser, workerfactory):
    self.argvparser = argvparser
    self.workerfactory = workerfactory

  def parseargv(self, argv):
    options, argvunknown = self.argvparser.parse(argv)
    return options, argvunknown

  def createworker(self, options, argvunknown):
    worker = self.workerfactory.produce(options, argvunknown)
    return worker

  def dowork(self, worker):
    exitstatus = worker()
    return exitstatus

  def tryrun(self, argv):
    options, argvunknown = self.parseargv(argv)
    worker = self.createworker(options, argvunknown)
    exitstatus = self.dowork(worker)
    return exitstatus

  def run(self, argv, stderr):
    try:
      exitstatus = self.tryrun(argv)
      return exitstatus
    except ArgvError as err:
      stderr.write(str(err) + '\n')
      return 2
    except Error as err:
      stderr.write(str(err) + '\n')
      return 1

def secludedmain(openfunc, stdout, stderr, argv):
  optionsdata = []
  argvparser = ArgvParser(getopt.getopt, optionsdata)
  jsonreader = JsonReader(openfunc, json.load)
  urlgeneratorfactory = UrlGeneratorFactory({
        'windowgenerator': WindowGenerator,
        'tabgenerator': TabGenerator,
        'urlgenerator': OpenUrlGenerator})
  urlwriter = UrlWriter(stdout)
  sessionstoreparser = SessionStoreParser(
        jsonreader, urlgeneratorfactory, urlwriter)
  workerfactory = WorkerFactory(sessionstoreparser, SessionStoreParserWorker)
  app = Application(argvparser, workerfactory)
  exitstatus = app.run(argv, stderr)
  return exitstatus

def main(): # pragma: no cover
  import sys
  exitstatus = secludedmain(open, sys.stdout, sys.stderr, sys.argv)
  return exitstatus
