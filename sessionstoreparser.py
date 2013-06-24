#! /usr/bin/env python

import json
import sys

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

  def __init__(self):
    pass

  def printopenurls(self, sessionstore):
    printer = OpenUrlPrinter(sys.stdout)
    printer.doprint(sessionstore)

  def main(self):
    if len(sys.argv) != 2:
      print 'need filename'
      return 1
    filename = sys.argv[1]
    fileob = open(filename)
    sessionstore = json.load(fileob)
    fileob.close()
    self.printopenurls(sessionstore)
    return 0

def main():
  main = Main()
  exitstatus = main.main()
  sys.exit(exitstatus)
