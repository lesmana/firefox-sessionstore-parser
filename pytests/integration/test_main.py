
import unittest

import contextlib
import StringIO
import textwrap

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_default(self):
    report = []
    fakefilecontent = textwrap.dedent('''\
          {
            "windows": [{
              "selected": 1,
              "tabs": [{
                "index": 1,
                "entries": [{
                  "url": "http://window1tab1url1"}]}],
              "_closedTabs": []}],
            "_closedWindows": []}''')
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(filename):
      report.append(('fakeopen', filename))
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), 'http://window1tab1url1\n')
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(report, [
          ('fakeopen', 'filename')])

  def test_noargv(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname']
    exitstatus = p.secludedmain(None, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 2)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'need filename\n')

  def test_notfile(self):
    report = []
    def fakeopen(filename):
      report.append(('fakeopen', filename))
      raise IOError('ignored error message')
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 1)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot open file filename.\n')
    self.assertEqual(report, [
          ('fakeopen', 'filename')])

  def test_notjson(self):
    report = []
    fakefilecontent = textwrap.dedent('''\
          what is this i don't even''')
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(filename):
      report.append(('fakeopen', filename))
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 1)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot read session store from file filename.\n')
    self.assertEqual(report, [
          ('fakeopen', 'filename')])
