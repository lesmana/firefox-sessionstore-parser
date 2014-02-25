#! /usr/bin/env python

import json

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

class ArgvError(Exception):
  pass

class ArgvHandler(object):
  def __init__(self):
    pass

  def handle(self, argv):
    if len(argv) != 2:
      success = False
      filename = None
      errormessage = 'need filename'
    else:
      success = True
      filename = argv[1]
      errormessage = None
    if not success:
      raise ArgvError(errormessage)
    return filename

class JsonReader(object):
  def __init__(self, openfunc):
    self.openfunc = openfunc

  def read(self, filename):
    with self.openfunc(filename) as fileob:
      sessionstore = json.load(fileob)
    return sessionstore

class UrlGeneratorFactory(object):
  def __init__(self):
    self.classes = {
          'windowgenerator': WindowGenerator,
          'tabgenerator': TabGenerator,
          'urlgenerator': OpenUrlGenerator}

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

class MainError(Exception):
  pass

class Main(object):

  def __init__(self, argvhandler, jsonreader, urlgeneratorfactory, urlwriter):
    self.argvhandler = argvhandler
    self.jsonreader = jsonreader
    self.urlgeneratorfactory = urlgeneratorfactory
    self.urlwriter = urlwriter

  def handleargv(self, argv):
    try:
      filename = self.argvhandler.handle(argv)
      return filename
    except ArgvError as ae:
      errormessage = str(ae)
      raise MainError(errormessage)

  def getsessionstore(self, filename):
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

  def trymain(self, argv):
    filename = self.handleargv(argv)
    sessionstore = self.getsessionstore(filename)
    urlgenerator = self.geturlgenerator()
    urls = self.geturls(urlgenerator, sessionstore)
    self.writeurls(urls)

  def main(self, argv):
    try:
      self.trymain(argv)
      return 0, None
    except MainError as me:
      return 1, str(me)

def main():
  import sys
  argvhandler = ArgvHandler()
  jsonreader = JsonReader(open)
  urlgeneratorfactory = UrlGeneratorFactory()
  urlwriter = UrlWriter(sys.stdout)
  main = Main(argvhandler, jsonreader, urlgeneratorfactory, urlwriter)
  exitstatus, errormessage = main.main(sys.argv)
  if errormessage is not None:
    sys.stderr.write(errormessage + '\n')
  return exitstatus
