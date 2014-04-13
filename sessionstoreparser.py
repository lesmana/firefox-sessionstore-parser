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

class ArgvHandler(object):
  def __init__(self):
    pass

  def handle(self, argv):
    shortopts = ''
    longopts = []
    opts, args = getopt.getopt(argv[1:], shortopts, longopts)
    if len(args) != 1:
      errormessage = 'need filename'
      raise ArgvError(errormessage)
    filename = args[0]
    return filename

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

class Application(object):

  def __init__(self, argvhandler, jsonreader, urlgeneratorfactory, urlwriter):
    self.argvhandler = argvhandler
    self.jsonreader = jsonreader
    self.urlgeneratorfactory = urlgeneratorfactory
    self.urlwriter = urlwriter

  def handleargv(self, argv):
    filename = self.argvhandler.handle(argv)
    return filename

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

  def tryrun(self, argv):
    filename = self.handleargv(argv)
    options = {'filename': filename}
    sessionstore = self.getsessionstore(options)
    urlgenerator = self.geturlgenerator()
    urls = self.geturls(urlgenerator, sessionstore)
    self.writeurls(urls)

  def run(self, argv):
    try:
      self.tryrun(argv)
      return 0, None
    except ArgvError as err:
      return 2, str(err)
    except Error as err:
      return 1, str(err)

def secludedmain(openfunc, stdout, stderr, argv):
  argvhandler = ArgvHandler()
  jsonreader = JsonReader(openfunc, json.load)
  urlgeneratorfactory = UrlGeneratorFactory({
        'windowgenerator': WindowGenerator,
        'tabgenerator': TabGenerator,
        'urlgenerator': OpenUrlGenerator})
  urlwriter = UrlWriter(stdout)
  app = Application(argvhandler, jsonreader, urlgeneratorfactory, urlwriter)
  exitstatus, errormessage = app.run(argv)
  if errormessage is not None:
    stderr.write(errormessage + '\n')
  return exitstatus

def main(): # pragma: no cover
  import sys
  exitstatus = secludedmain(open, sys.stdout, sys.stderr, sys.argv)
  return exitstatus
