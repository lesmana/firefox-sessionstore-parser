
import unittest

import contextlib
import os
import StringIO
import textwrap

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_default(self):
    fakefilecontent = textwrap.dedent('''\
          {
            "windows": [
              {
                "tabs": [
                  {
                    "index": 1,
                    "entries": [
                      {
                        "url": "http://window1tab1url1"
                      }
                    ]
                  }
                ],
                "selected": 1,
                "_closedTabs": []
              }
            ],
            "_closedWindows": [],
            "selectedWindow": 0
          }
          ''')
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), 'http://window1tab1url1\n')
    self.assertEqual(fakestderr.getvalue(), '')

  def test_noargv(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, None)
    self.assertEqual(exitstatus, 2)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'missing argument: filename\n')

  def test_wrongargv(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--wrong']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, None)
    self.assertEqual(exitstatus, 2)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'unknown option: --wrong\n')

  def test_notfile(self):
    def fakeopen(dummy_filename):
      raise IOError('ignored error message')
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(exitstatus, 1)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot open file filename.\n')

  def test_notjson(self):
    fakefilecontent = textwrap.dedent('''\
          what is this i don't even''')
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(exitstatus, 1)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot read session store from file filename.\n')

def gettestdata():
  filename = os.path.join(os.path.dirname(__file__), 'testdata.js')
  with open(filename) as testdatafile:
    testdata = testdatafile.read()
  return testdata

class TestMainRealData(unittest.TestCase):

  testdata = gettestdata()

  def test_default(self):
    fakefile = StringIO.StringIO(self.testdata)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://w1t1u3/
          http://w1t2u2/
          http://w1t3u1/
          http://w2t1u3/
          http://w2t2u2/
          http://w2t3u1/
          http://w3t1u3/
          http://w3t2u2/
          http://w3t3u1/
          '''))
    self.assertEqual(fakestderr.getvalue(), '')

  def test_all(self):
    fakefile = StringIO.StringIO(self.testdata)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--all', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://w1t1u1b2/
          http://w1t1u2b1/
          http://w1t1u3/
          http://w1t2u1b1/
          http://w1t2u2/
          http://w1t2u3f1/
          http://w1t3u1/
          http://w1t3u2f1/
          http://w1t3u3f2/
          http://w1ct1u1b1/
          http://w1ct1u2/
          http://w1ct2u1/
          http://w1ct2u2f1/
          http://w2t1u1b2/
          http://w2t1u2b1/
          http://w2t1u3/
          http://w2t2u1b1/
          http://w2t2u2/
          http://w2t2u3f1/
          http://w2t3u1/
          http://w2t3u2f1/
          http://w2t3u3f2/
          http://w2ct1u1b1/
          http://w2ct1u2/
          http://w2ct2u1/
          http://w2ct2u2f1/
          http://w3t1u1b2/
          http://w3t1u2b1/
          http://w3t1u3/
          http://w3t2u1b1/
          http://w3t2u2/
          http://w3t2u3f1/
          http://w3t3u1/
          http://w3t3u2f1/
          http://w3t3u3f2/
          http://w3ct1u1b1/
          http://w3ct1u2/
          http://w3ct2u1/
          http://w3ct2u2f1/
          http://cw1t1u1b1
          http://cw1t1u2
          http://cw1t2u1
          http://cw1t2u2f1
          http://cw1ct1u1b1/
          http://cw1ct1u2/
          http://cw1ct2u1/
          http://cw1ct2u2f1/
          http://cw2t1u1b1
          http://cw2t1u2
          http://cw2t2u1
          http://cw2t2u2f1
          http://cw2ct1u1b1/
          http://cw2ct1u2/
          http://cw2ct2u1/
          http://cw2ct2u2f1/
          '''))
    self.assertEqual(fakestderr.getvalue(), '')
