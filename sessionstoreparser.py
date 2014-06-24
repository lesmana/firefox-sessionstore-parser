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

class HelpPrinter(object):
  def __init__(self, stream, message, exitstatus):
    self.stream = stream
    self.message = message
    self.exitstatus = exitstatus

  def __call__(self):
    self.stream.write(self.message + '\n')
    return self.exitstatus

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

class SessionStoreProducer(object):
  def __init__(self, jsonreader, filename):
    self.jsonreader = jsonreader
    self.filename = filename

  def produce(self):
    return self.jsonreader.read(self.filename)

class UrlProducer(object):
  def __init__(self):
    pass

  def handleentry(self, entry):
    plainurl = entry['url']
    url = {'url': plainurl}
    yield url

  def handletab(self, tab):
    openindex = tab['index'] - 1
    entries = tab['entries']
    for index, entry in enumerate(entries):
      for url in self.handleentry(entry):
        url['urlindex'] = index
        url['openindex'] = openindex
        yield url

  def handlewindow(self, window):
    for tab in window['tabs']:
      for url in self.handletab(tab):
        url['tab'] = 'open'
        yield url
    for tab in window['_closedTabs']:
      for url in self.handletab(tab['state']):
        url['tab'] = 'closed'
        yield url

  def handlesessionstore(self, sessionstore):
    for window in sessionstore['windows']:
      for url in self.handlewindow(window):
        url['window'] = 'open'
        yield url
    for window in sessionstore['_closedWindows']:
      for url in self.handlewindow(window):
        url['window'] = 'closed'
        yield url

  def generate(self, sessionstore):
    for url in self.handlesessionstore(sessionstore):
      yield url

  def produce(self, sessionstore):
    return self.generate(sessionstore)

class OpenUrlPredicate(object):
  def __init__(self):
    pass

  def isgood(self, url):
    if url['tab'] == 'closed':
      return False
    if url['window'] == 'closed':
      return False
    index = url['urlindex']
    openindex = url['openindex']
    if index == openindex:
      return True

class AllUrlPredicate(object):
  def __init__(self):
    pass

  def isgood(self, url):
    return True

class UrlFilter(object):
  def __init__(self, predicate):
    self.predicate = predicate

  def filter(self, urls):
    for url in urls:
      if self.predicate.isgood(url):
        yield url

class UrlWriter(object):
  def __init__(self, stdout):
    self.stdout = stdout

  def write(self, urls):
    for url in urls:
      self.stdout.write(url['url'] + '\n')

  def consume(self, urls):
    self.write(urls)

class SessionStoreParser(object):
  def __init__(self,
        sessionstoreproducer, urlproducer, urlfilter, urlconsumer):
    self.sessionstoreproducer = sessionstoreproducer
    self.urlproducer = urlproducer
    self.urlfilter = urlfilter
    self.urlconsumer = urlconsumer

  def parse(self):
    sessionstore = self.sessionstoreproducer.produce()
    urls = self.urlproducer.produce(sessionstore)
    filteredurls = self.urlfilter.filter(urls)
    self.urlconsumer.consume(filteredurls)

  def __call__(self):
    self.parse()
    return 0

class HelpPrinterFactory(object):
  def __init__(self, helpprinterclass, stderr):
    self.helpprinterclass = helpprinterclass
    self.stderr = stderr

  def produce(self, message):
    worker = self.helpprinterclass(self.stderr, message, 2)
    return worker

class SessionStoreProducerFactory(object):
  def __init__(self, jsonreaderclass, sessionstoreproducerclass, openfunc):
    self.jsonreaderclass = jsonreaderclass
    self.sessionstoreproducerclass = sessionstoreproducerclass
    self.openfunc = openfunc

  def produce(self, parsedargv):
    filename = parsedargv['filename']
    jsonreader = self.jsonreaderclass(self.openfunc, json.load)
    sessionstoreproducer = self.sessionstoreproducerclass(jsonreader, filename)
    return sessionstoreproducer

class UrlProducerFactory(object):
  def __init__(self, urlproducerclass):
    self.urlproducerclass = urlproducerclass

  def produce(self, parsedargv):
    urlproducer = self.urlproducerclass()
    return urlproducer

class UrlFilterFactory(object):
  def __init__(self, urlfilterclass):
    self.urlfilterclass = urlfilterclass

  def produce(self, parsedargv):
    if 'all' in parsedargv:
      predicateclass = AllUrlPredicate
    else:
      predicateclass = OpenUrlPredicate
    predicate = predicateclass()
    urlfilter = self.urlfilterclass(predicate)
    return urlfilter

class UrlConsumerFactory(object):
  def __init__(self, urlconsumerclass, stdout):
    self.urlconsumerclass = urlconsumerclass
    self.stdout = stdout

  def produce(self, parsedargv):
    urlconsumer = self.urlconsumerclass(self.stdout)
    return urlconsumer

class SessionStoreParserFactory(object):
  def __init__(self,
        sessionstoreproducerfactory,
        urlproducerfactory,
        urlfilterfactory,
        urlconsumerfactory,
        sessionstoreparserclass):
    self.sessionstoreproducerfactory = sessionstoreproducerfactory
    self.urlproducerfactory = urlproducerfactory
    self.urlfilterfactory = urlfilterfactory
    self.urlconsumerfactory = urlconsumerfactory
    self.sessionstoreparserclass = sessionstoreparserclass

  def produce(self, parsedargv):
    sessionstoreproducer = self.sessionstoreproducerfactory.produce(parsedargv)
    urlproducer = self.urlproducerfactory.produce(parsedargv)
    urlfilter = self.urlfilterfactory.produce(parsedargv)
    urlconsumer = self.urlconsumerfactory.produce(parsedargv)
    sessionstoreparser = self.sessionstoreparserclass(
          sessionstoreproducer, urlproducer, urlfilter, urlconsumer)
    return sessionstoreparser

class WorkerFactory(object):
  def __init__(self, helpprinterfactory, sessionstoreparserfactory):
    self.helpprinterfactory = helpprinterfactory
    self.sessionstoreparserfactory = sessionstoreparserfactory

  def checkparsedargv(self, parsedargv):
    if 'unknown' in parsedargv:
      unknownoption = parsedargv['unknown'][0]
      message = 'unknown option: %s' % (unknownoption)
    elif 'filename' not in parsedargv:
      message = 'missing argument: filename'
    else:
      return False, None
    return True, message

  def produce(self, parsedargv):
    errorfound, message = self.checkparsedargv(parsedargv)
    if errorfound:
      worker = self.helpprinterfactory.produce(message)
    else:
      worker = self.sessionstoreparserfactory.produce(parsedargv)
    return worker

class Application(object):

  def __init__(self, argvparser, workerfactory, stderr):
    self.argvparser = argvparser
    self.workerfactory = workerfactory
    self.stderr = stderr

  def tryrun(self, argv):
    parsedargv = self.argvparser.parse(argv)
    worker = self.workerfactory.produce(parsedargv)
    exitstatus = worker()
    return exitstatus

  def run(self, argv):
    try:
      exitstatus = self.tryrun(argv)
      return exitstatus
    except Error as err:
      self.stderr.write(str(err) + '\n')
      return 1

class ApplicationFactory(object):
  def __init__(self, stdout, stderr, openfunc):
    self.stdout = stdout
    self.stderr = stderr
    self.openfunc = openfunc

  def produce(self, optionsdata=None, argumentsdata=None, **classes):
    if optionsdata is None:
      optionsdata = [
            ('all', ['--all'], 0)]
    if argumentsdata is None:
      argumentsdata = [
            'filename']
    helpprinterclass = classes.get(
          'HelpPrinter', HelpPrinter)
    jsonreaderclass = classes.get(
          'JsonReader', JsonReader)
    sessionstoreproducerclass = classes.get(
          'SessionStoreProducer', SessionStoreProducer)
    urlproducerclass = classes.get(
          'UrlProducer', UrlProducer)
    urlfilterclass = classes.get(
          'UrlFilter', UrlFilter)
    urlwriterclass = classes.get(
          'UrlWriter', UrlWriter)
    sessionstoreparserclass = classes.get(
          'SessionStoreParser', SessionStoreParser)
    argvparser = ArgvParser(
          getopt.getopt,
          optionsdata,
          argumentsdata)
    helpprinterfactory = HelpPrinterFactory(
          helpprinterclass,
          self.stderr)
    sessionstoreproducerfactory = SessionStoreProducerFactory(
          jsonreaderclass,
          sessionstoreproducerclass,
          self.openfunc)
    urlproducerfactory = UrlProducerFactory(
          urlproducerclass)
    urlfilterfactory = UrlFilterFactory(
          urlfilterclass)
    urlconsumerfactory = UrlConsumerFactory(
          urlwriterclass,
          self.stdout)
    sessionstoreparserfactory = SessionStoreParserFactory(
          sessionstoreproducerfactory,
          urlproducerfactory,
          urlfilterfactory,
          urlconsumerfactory,
          sessionstoreparserclass)
    workerfactory = WorkerFactory(
          helpprinterfactory,
          sessionstoreparserfactory)
    app = Application(
          argvparser,
          workerfactory,
          self.stderr)
    return app

def secludedmain(argv, stdout, stderr, openfunc):
  appfactory = ApplicationFactory(stdout, stderr, openfunc)
  app = appfactory.produce()
  exitstatus = app.run(argv)
  return exitstatus

def main(): # pragma: no cover
  import sys
  exitstatus = secludedmain(sys.argv, sys.stdout, sys.stderr, open)
  return exitstatus
