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

  def __init__(self):
    pass

  def parse(self, sessionstore):
    self.windowsgenerator = WindowsGenerator()
    self.tabgenerator = TabGenerator()
    self.openurlgenerator = OpenUrlGenerator()
    for windows in self.windowsgenerator.generate(sessionstore):
      for tab in self.tabgenerator.generate(windows):
        for url in self.openurlgenerator.generate(tab):
          yield url

class Main(object):

  def __init__(self, stdout, openfunc):
    self.stdout = stdout
    self.openfunc = openfunc

  def getsessionstore(self, filename):
    with self.openfunc(filename) as fileob:
      sessionstore = json.load(fileob)
    return sessionstore

  def getparser(self):
    parser = Parser()
    return parser

  def printurls(self, parser, sessionstore):
    for url in parser.parse(sessionstore):
      self.stdout.write(url + '\n')

  def main(self, argv):
    if len(argv) != 2:
      self.stdout.write('need filename')
      return 1
    filename = argv[1]
    sessionstore = self.getsessionstore(filename)
    parser = self.getparser()
    self.printurls(parser, sessionstore)
    return 0

def main():
  import sys
  main = Main(sys.stdout, open)
  exitstatus = main.main(sys.argv)
  sys.exit(exitstatus)
