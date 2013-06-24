#! /usr/bin/env python

import json

class OpenUrlPrinter(object):

  def __init__(self, stdout):
    self.stdout = stdout

  def doprint(self, sessionstore):
    for windows in sessionstore['windows']:
      for tab in windows['tabs']:
        openindex = tab['index'] - 1
        openentry = tab['entries'][openindex]
        openurl = openentry['url']
        self.stdout.write(openurl + '\n')

class Main(object):

  def __init__(self, stdout, openfunc):
    self.stdout = stdout
    self.openfunc = openfunc

  def getsessionstore(self, filename):
    fileob = self.openfunc(filename)
    sessionstore = json.load(fileob)
    fileob.close()
    return sessionstore

  def printopenurls(self, sessionstore):
    printer = OpenUrlPrinter(self.stdout)
    printer.doprint(sessionstore)

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
