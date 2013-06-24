#! /usr/bin/env python

import json

class OpenUrlGenerator(object):

  def __init__(self):
    pass

  def generate(self, sessionstore):
    for windows in sessionstore['windows']:
      for tab in windows['tabs']:
        openindex = tab['index'] - 1
        openentry = tab['entries'][openindex]
        openurl = openentry['url']
        yield openurl

class Main(object):

  def __init__(self, stdout, openfunc):
    self.stdout = stdout
    self.openfunc = openfunc

  def getsessionstore(self, filename):
    with self.openfunc(filename) as fileob:
      sessionstore = json.load(fileob)
    return sessionstore

  def printopenurls(self, sessionstore):
    generator = OpenUrlGenerator()
    for url in generator.generate(sessionstore):
      self.stdout.write(url + '\n')

  def main(self, argv):
    if len(argv) != 2:
      print 'need filename'
      return 1
    filename = argv[1]
    sessionstore = self.getsessionstore(filename)
    self.printopenurls(sessionstore)
    return 0

def main():
  import sys
  main = Main(sys.stdout, open)
  exitstatus = main.main(sys.argv)
  sys.exit(exitstatus)
