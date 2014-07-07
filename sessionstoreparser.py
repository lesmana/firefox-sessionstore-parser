#! /usr/bin/env python

"""
here be module documentation.
"""

VERSION = '0.9'

COMMANDNAME = 'sessionstoreparser'

USAGE = '''\
{commandname} {version}
usage: {commandname} [options] filename
without options will show selected urls from open tabs from open windows.
'''.format(commandname=COMMANDNAME, version=VERSION)

SHORTHELP = USAGE + '''\
for list of options use {commandname} -h
'''.format(commandname=COMMANDNAME)

HELP = USAGE + '''\
options:
  --all                  selected urls from all tabs from all windows
  --all-with-history     like above but show all urls
  --selected             selected urls from selected tabs from selected windows
  --closed               selected urls from closed tabs from closed windows
  --closed-with-history  like above but show all urls
  --window=STATE         open, closed, selected, all; default: open
  --tab=STATE            open, closed, selected, all; default: open
  --url=STATE            back, selected, forward, all; default: selected
  -h, --help             print this help
  --version              print version
'''

import getopt
import json

class Error(Exception):
  pass

class ArgvError(Error):
  pass

class ArgvParser(object):
  def __init__(self, getoptfunc, optionsdata, argumentsdata):
    self.getoptfunc = getoptfunc
    self.optionsdata = optionsdata
    self.argumentsdata = argumentsdata

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

  def prepareoptionsdata(self, optionsdata):
    # no error checking
    # let's assume everyone is sane
    shortoptslist = []
    longopts = []
    optnames = {}
    for name, opts, argcount in optionsdata:
      for opt in opts:
        shorts, longs = self.prepareopt(opt, argcount)
        shortoptslist.extend(shorts)
        longopts.extend(longs)
        optnames[opt] = name
    shortopts = ''.join(shortoptslist)
    return shortopts, longopts, optnames

  def dictifyopts(self, opts, optnames):
    optsdict = {}
    for opt, val in opts:
      name = optnames[opt]
      optsdict[name] = val
    return optsdict

  def splitopts(self, argv):
    shortopts, longopts, optnames = self.prepareoptionsdata(self.optionsdata)
    opts, args = self.getoptfunc(argv, shortopts, longopts)
    optsdict = self.dictifyopts(opts, optnames)
    return optsdict, args

  def splitargs(self, args):
    argsdict = {}
    restargv = args
    for name in self.argumentsdata:
      if len(restargv) > 0:
        arg = restargv[0]
        restargv = restargv[1:]
        argsdict[name] = arg
      else:
        break
    return argsdict, restargv

  def combine(self, optsdict, argsdict):
    parsedargv = {}
    parsedargv.update(optsdict)
    parsedargv.update(argsdict)
    return parsedargv

  def tryparse(self, argv):
    optsdict, args = self.splitopts(argv)
    argsdict, restargv = self.splitargs(args)
    parsedargv = self.combine(optsdict, argsdict)
    return parsedargv, restargv

  def parse(self, argv):
    try:
      parsedargv, restargv = self.tryparse(argv)
    except getopt.GetoptError as err:
      parsedargv = {}
      unknownoption = str(err).split()[1]
      restargv = [unknownoption]
    return parsedargv, restargv

class JsonReader(object):
  def __init__(self, openfunc, jsonloadfunc):
    self.openfunc = openfunc
    self.jsonloadfunc = jsonloadfunc

  def openfile(self, filename):
    try:
      fileob = self.openfunc(filename)
      return fileob
    except IOError:
      raise Error('error: cannot open file %s.' % filename)

  def jsonload(self, fileob, filename):
    try:
      sessionstore = self.jsonloadfunc(fileob)
      return sessionstore
    except ValueError:
      raise Error('error: cannot read session store from file %s.' % filename)

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

class SessionStoreProducerFactory(object):
  def __init__(self, jsonreaderclass, sessionstoreproducerclass,
        openfunc, jsonloadfunc):
    self.jsonreaderclass = jsonreaderclass
    self.sessionstoreproducerclass = sessionstoreproducerclass
    self.openfunc = openfunc
    self.jsonloadfunc = jsonloadfunc

  def make(self, parsedargv):
    try:
      filename = parsedargv['filename']
    except KeyError:
      raise ArgvError('missing argument: filename')
    jsonreader = self.jsonreaderclass(self.openfunc, self.jsonloadfunc)
    sessionstoreproducer = self.sessionstoreproducerclass(jsonreader, filename)
    return sessionstoreproducer

class UrlProducer(object):
  def __init__(self):
    pass

  def handleentry(self, entry):
    plainurl = entry['url']
    url = {
          'window': set(),
          'tab': set(),
          'entry': set(),
          'url': plainurl}
    yield url

  def handletab(self, tab):
    openindex = tab['index'] - 1
    entries = tab['entries']
    for index, entry in enumerate(entries):
      for url in self.handleentry(entry):
        if index < openindex:
          url['entry'].add('back')
        elif index > openindex:
          url['entry'].add('forward')
        else: # index == openindex:
          url['entry'].add('selected')
        yield url

  def handlewindow(self, window):
    selected = window['selected'] - 1
    for index, tab in enumerate(window['tabs']):
      for url in self.handletab(tab):
        url['tab'].add('open')
        if index == selected:
          url['tab'].add('selected')
        yield url
    for tab in window['_closedTabs']:
      for url in self.handletab(tab['state']):
        url['tab'].add('closed')
        yield url

  def handlesessionstore(self, sessionstore):
    selected = sessionstore['selectedWindow'] - 1
    for index, window in enumerate(sessionstore['windows']):
      for url in self.handlewindow(window):
        url['window'].add('open')
        if index == selected:
          url['window'].add('selected')
        yield url
    for window in sessionstore['_closedWindows']:
      for url in self.handlewindow(window):
        url['window'].add('closed')
        yield url

  def generate(self, sessionstore):
    for url in self.handlesessionstore(sessionstore):
      yield url

  def produce(self, sessionstore):
    return self.generate(sessionstore)

class UrlProducerFactory(object):
  def __init__(self, urlproducerclass):
    self.urlproducerclass = urlproducerclass

  def make(self, parsedargv):
    #pylint: disable=unused-argument
    urlproducer = self.urlproducerclass()
    return urlproducer

class UrlFilter(object):
  def __init__(self, attributes):
    self.attributes = attributes

  def attributesmatch(self, url):
    for key, value in self.attributes.items():
      if url[key].isdisjoint(value):
        return False
    return True

  def filter(self, urls):
    for url in urls:
      if self.attributesmatch(url):
        yield url

class UrlFilterFactory(object):
  def __init__(self, urlfilterclass,
        defaulttemplates, optionstemplates, attributes):
    self.urlfilterclass = urlfilterclass
    self.defaulttemplates = defaulttemplates
    self.optionstemplates = optionstemplates
    self.attributes = attributes

  def gettemplates(self, parsedargv):
    templates = {}
    templates.update(self.defaulttemplates)
    for option, template in self.optionstemplates.items():
      if option in parsedargv:
        templates.update(template)
    for name in templates:
      if name in parsedargv:
        templates[name] = parsedargv[name]
    return templates

  def getattributes(self, templates):
    attributes = {}
    for name, template in templates.items():
      if template in self.attributes[name]:
        attributes[name] = self.attributes[name][template]
      else:
        raise ArgvError('illegal value for "%s": "%s"' % (name, template))
    return attributes

  def make(self, parsedargv):
    templates = self.gettemplates(parsedargv)
    attributes = self.getattributes(templates)
    urlfilter = self.urlfilterclass(attributes)
    return urlfilter

class UrlWriter(object):
  def __init__(self, stream):
    self.stream = stream

  def write(self, urls):
    for url in urls:
      self.stream.write(url['url'] + '\n')

  def consume(self, urls):
    self.write(urls)

class UrlConsumerFactory(object):
  def __init__(self, urlconsumerclass, stream):
    self.urlconsumerclass = urlconsumerclass
    self.stream = stream

  def make(self, parsedargv):
    #pylint: disable=unused-argument
    urlconsumer = self.urlconsumerclass(self.stream)
    return urlconsumer

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

class SessionStoreParserFactory(object):
  def __init__(self,
        sessionstoreproducerfactory,
        urlproducerfactory,
        urlfilterfactory,
        urlconsumerfactory,
        sessionstoreparserclass):
    #pylint: disable=too-many-arguments
    self.sessionstoreproducerfactory = sessionstoreproducerfactory
    self.urlproducerfactory = urlproducerfactory
    self.urlfilterfactory = urlfilterfactory
    self.urlconsumerfactory = urlconsumerfactory
    self.sessionstoreparserclass = sessionstoreparserclass

  def make(self, parsedargv):
    sessionstoreproducer = self.sessionstoreproducerfactory.make(parsedargv)
    urlproducer = self.urlproducerfactory.make(parsedargv)
    urlfilter = self.urlfilterfactory.make(parsedargv)
    urlconsumer = self.urlconsumerfactory.make(parsedargv)
    sessionstoreparser = self.sessionstoreparserclass(
          sessionstoreproducer, urlproducer, urlfilter, urlconsumer)
    return sessionstoreparser

class Application(object):

  def __init__(self, argvparser, sessionstoreparserfactory, stdout, stderr):
    self.argvparser = argvparser
    self.sessionstoreparserfactory = sessionstoreparserfactory
    self.stdout = stdout
    self.stderr = stderr

  def tryrun(self, argv):
    parsedargv, restargv = self.argvparser.parse(argv[1:])
    if 'help' in parsedargv:
      self.stdout.write(HELP)
    elif len(restargv) != 0:
      unknownoption = restargv[0]
      message = 'unknown option: %s' % (unknownoption)
      raise ArgvError(message)
    elif len(parsedargv) == 0:
      self.stdout.write(SHORTHELP)
    elif 'version' in parsedargv:
      self.stdout.write(VERSION + '\n')
    else:
      sessionstoreparser = self.sessionstoreparserfactory.make(parsedargv)
      sessionstoreparser.parse()

  def run(self, argv):
    try:
      self.tryrun(argv)
      exitstatus = 0
    except ArgvError as err:
      self.stderr.write(str(err) + '\n')
      exitstatus = 2
    except Error as err:
      self.stderr.write(str(err) + '\n')
      exitstatus = 1
    return exitstatus

class ApplicationFactory(object):
  def __init__(self, stdout, stderr, openfunc):
    self.stdout = stdout
    self.stderr = stderr
    self.openfunc = openfunc

  def getdefaults(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('version', ['--version'], 0),
          ('all', ['--all'], 0),
          ('allwithhistory', ['--all-with-history'], 0),
          ('selected', ['--selected'], 0),
          ('closed', ['--closed'], 0),
          ('closedwithhistory', ['--closed-with-history'], 0),
          ('window', ['--window'], 1),
          ('tab', ['--tab'], 1),
          ('entry', ['--url'], 1)]
    argumentsdata = [
          'filename']
    defaulttemplates = {
          'window': 'default',
          'tab': 'default',
          'entry': 'default'}
    optionstemplates = {
          'all': {
            'window': 'all',
            'tab': 'all'},
          'allwithhistory': {
            'window': 'all',
            'tab': 'all',
            'entry': 'all'},
          'selected': {
            'window': 'selected',
            'tab': 'selected'},
          'closed': {
            'window': 'closed',
            'tab': 'closed'},
          'closedwithhistory': {
            'window': 'closed',
            'tab': 'closed',
            'entry': 'all'}}
    attributes = {
          'window': {
            'default': ['open'],
            'all': ['open', 'closed'],
            'open': ['open'],
            'selected': ['selected'],
            'closed': ['closed']},
          'tab': {
            'default': ['open'],
            'all': ['open', 'closed'],
            'open': ['open'],
            'selected': ['selected'],
            'closed': ['closed']},
          'entry': {
            'default': ['selected'],
            'all': ['back', 'selected', 'forward'],
            'back': ['back'],
            'selected': ['selected'],
            'forward': ['forward']}}
    defaults = {
          'optionsdata': optionsdata,
          'argumentsdata': argumentsdata,
          'defaulttemplates': defaulttemplates,
          'optionstemplates': optionstemplates,
          'attributes': attributes,
          'getoptfunc': getopt.getopt,
          'jsonloadfunc': json.load,
          'argvparserclass': ArgvParser,
          'jsonreaderclass': JsonReader,
          'sessionstoreproducerfactoryclass': SessionStoreProducerFactory,
          'sessionstoreproducerclass': SessionStoreProducer,
          'urlproducerfactoryclass': UrlProducerFactory,
          'urlproducerclass': UrlProducer,
          'urlfilterfactoryclass': UrlFilterFactory,
          'urlfilterclass': UrlFilter,
          'urlconsumerfactoryclass': UrlConsumerFactory,
          'urlwriterclass': UrlWriter,
          'sessionstoreparserfactoryclass': SessionStoreParserFactory,
          'sessionstoreparserclass': SessionStoreParser,
          'applicationclass': Application}
    return defaults

  def make(self, optionsdata, argumentsdata,
        defaulttemplates,
        optionstemplates,
        attributes,
        getoptfunc,
        jsonloadfunc,
        argvparserclass,
        jsonreaderclass,
        sessionstoreproducerfactoryclass,
        sessionstoreproducerclass,
        urlproducerfactoryclass,
        urlproducerclass,
        urlfilterfactoryclass,
        urlfilterclass,
        urlconsumerfactoryclass,
        urlwriterclass,
        sessionstoreparserfactoryclass,
        sessionstoreparserclass,
        applicationclass):
    #pylint: disable=too-many-arguments
    #pylint: disable=too-many-locals
    #pylint: disable=invalid-name
    argvparser = argvparserclass(
          getoptfunc,
          optionsdata,
          argumentsdata)
    sessionstoreproducerfactory = sessionstoreproducerfactoryclass(
          jsonreaderclass,
          sessionstoreproducerclass,
          self.openfunc,
          jsonloadfunc)
    urlproducerfactory = urlproducerfactoryclass(
          urlproducerclass)
    urlfilterfactory = urlfilterfactoryclass(
          urlfilterclass,
          defaulttemplates,
          optionstemplates,
          attributes)
    urlconsumerfactory = urlconsumerfactoryclass(
          urlwriterclass,
          self.stdout)
    sessionstoreparserfactory = sessionstoreparserfactoryclass(
          sessionstoreproducerfactory,
          urlproducerfactory,
          urlfilterfactory,
          urlconsumerfactory,
          sessionstoreparserclass)
    app = applicationclass(
          argvparser,
          sessionstoreparserfactory,
          self.stdout,
          self.stderr)
    return app

  def makedefaults(self):
    defaults = self.getdefaults()
    app = self.make(**defaults)
    return app

def secludedmain(argv, stdout, stderr, openfunc):
  appfactory = ApplicationFactory(stdout, stderr, openfunc)
  app = appfactory.makedefaults()
  exitstatus = app.run(argv)
  return exitstatus

def main(): # pragma: no cover
  import sys
  exitstatus = secludedmain(sys.argv, sys.stdout, sys.stderr, open)
  return exitstatus
