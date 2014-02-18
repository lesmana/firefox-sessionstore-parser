#! /usr/bin/env python

import json

class WindowsGenerator(object):
  def __init__(self):
    pass

  def generate(self, sessionstore):
    for windows in sessionstore['windows']:
      yield windows

class TabGenerator(object):
  def __init__(self):
    pass

  def generate(self, windows):
    for tab in windows['tabs']:
      yield tab

class OpenUrlGenerator(object):
  def __init__(self):
    pass

  def generate(self, tab):
    openindex = tab['index'] - 1
    openentry = tab['entries'][openindex]
    openurl = openentry['url']
    yield openurl

class Parser(object):
  def __init__(self, windowsgenerator, tabgenerator, urlgenerator):
    self.windowsgenerator = windowsgenerator
    self.tabgenerator = tabgenerator
    self.urlgenerator = urlgenerator

  def parse(self, sessionstore):
    for windows in self.windowsgenerator.generate(sessionstore):
      for tab in self.tabgenerator.generate(windows):
        for url in self.urlgenerator.generate(tab):
          yield url

class ArgvHandler(object):
  def __init__(self):
    pass

  def handle(self, argv):
    if len(argv) != 2:
      success = False
      filename = None
      errormessage = 'need filename\n'
    else:
      success = True
      filename = argv[1]
      errormessage = None
    return success, filename, errormessage

class SessionStoreReader(object):
  def __init__(self, openfunc):
    self.openfunc = openfunc

  def read(self, filename):
    with self.openfunc(filename) as fileob:
      sessionstore = json.load(fileob)
    return sessionstore

class ParserFactory(object):
  def __init__(self):
    pass

  def produce(self):
    windowsgenerator = WindowsGenerator()
    tabgenerator = TabGenerator()
    urlgenerator = OpenUrlGenerator()
    parser = Parser(windowsgenerator, tabgenerator, urlgenerator)
    return parser

class Writer(object):
  def __init__(self, stdout):
    self.stdout = stdout

  def write(self, parser, sessionstore):
    for url in parser.parse(sessionstore):
      self.stdout.write(url + '\n')

class Main(object):

  def __init__(self, stdout, openfunc):
    self.stdout = stdout
    self.openfunc = openfunc
    self.argvhandler = ArgvHandler()
    self.sessionstorereader = SessionStoreReader(self.openfunc)
    self.parserfactory = ParserFactory()
    self.writer = Writer(self.stdout)

  def handleargv(self, argv):
    success, filename, errormessage = self.argvhandler.handle(argv)
    if not success:
      self.stdout.write(errormessage)
    return success, filename

  def getsessionstore(self, filename):
    sessionstore = self.sessionstorereader.read(filename)
    return sessionstore

  def getparser(self):
    parser = self.parserfactory.produce()
    return parser

  def printurls(self, parser, sessionstore):
    self.writer.write(parser, sessionstore)

  def trymain(self, argv):
    success, filename = self.handleargv(argv)
    if not success:
      return 1
    sessionstore = self.getsessionstore(filename)
    parser = self.getparser()
    self.printurls(parser, sessionstore)
    return 0

  def main(self, argv):
    return self.trymain(argv)

def main():
  import sys
  main = Main(sys.stdout, open)
  exitstatus = main.main(sys.argv)
  return exitstatus
