#! /usr/bin/env python

import json
import sys

def printopenurls(sessionstore):
  for windows in sessionstore['windows']:
    for tab in windows['tabs']:
      openindex = tab['index'] - 1
      openentry = tab['entries'][openindex]
      openurl = openentry['url']
      print openurl

def main():
  if len(sys.argv) != 2:
    print 'need filename'
    sys.exit(1)
  filename = sys.argv[1]
  fileob = open(filename)
  sessionstore = json.load(fileob)
  fileob.close()
  printopenurls(sessionstore)
