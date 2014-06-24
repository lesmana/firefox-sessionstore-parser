
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
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), 'http://window1tab1url1\n')
    self.assertEqual(exitstatus, 0)

  def test_noargv(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, None)
    self.assertEqual(fakestderr.getvalue(),
          'missing argument: filename\n')
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(exitstatus, 2)

  def test_wrongargv(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--wrong']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, None)
    self.assertEqual(fakestderr.getvalue(),
          'unknown option: --wrong\n')
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(exitstatus, 2)

  def test_notfile(self):
    def fakeopen(dummy_filename):
      raise IOError('ignored error message')
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot open file filename.\n')
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(exitstatus, 1)

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
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot read session store from file filename.\n')
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(exitstatus, 1)

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
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://ow1ot1s0u3/
          http://ow1ot2s0u2/
          http://ow1ot3s0u1/
          http://ow2ot1s0u3/
          http://ow2ot2s0u2/
          http://ow2ot3s0u1/
          http://ow3ot1s0u3/
          http://ow3ot2s0u2/
          http://ow3ot3s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_all(self):
    fakefile = StringIO.StringIO(self.testdata)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--all', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://ow1ot1s0u3/
          http://ow1ot2s0u2/
          http://ow1ot3s0u1/
          http://ow1ct1s0u2/
          http://ow1ct2s0u1/
          http://ow2ot1s0u3/
          http://ow2ot2s0u2/
          http://ow2ot3s0u1/
          http://ow2ct1s0u2/
          http://ow2ct2s0u1/
          http://ow3ot1s0u3/
          http://ow3ot2s0u2/
          http://ow3ot3s0u1/
          http://ow3ct1s0u2/
          http://ow3ct2s0u1/
          http://cw1ot1s0u2/
          http://cw1ot2s0u1/
          http://cw1ct1s0u2/
          http://cw1ct2s0u1/
          http://cw2ot1s0u2/
          http://cw2ot2s0u1/
          http://cw2ct1s0u2/
          http://cw2ct2s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_allwithhistory(self):
    fakefile = StringIO.StringIO(self.testdata)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--all-with-history', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://ow1ot1b2u1/
          http://ow1ot1b1u2/
          http://ow1ot1s0u3/
          http://ow1ot2b1u1/
          http://ow1ot2s0u2/
          http://ow1ot2f1u3/
          http://ow1ot3s0u1/
          http://ow1ot3f1u2/
          http://ow1ot3f2u3/
          http://ow1ct1b1u1/
          http://ow1ct1s0u2/
          http://ow1ct2s0u1/
          http://ow1ct2f1u2/
          http://ow2ot1b2u1/
          http://ow2ot1b1u2/
          http://ow2ot1s0u3/
          http://ow2ot2b1u1/
          http://ow2ot2s0u2/
          http://ow2ot2f1u3/
          http://ow2ot3s0u1/
          http://ow2ot3f1u2/
          http://ow2ot3f2u3/
          http://ow2ct1b1u1/
          http://ow2ct1s0u2/
          http://ow2ct2s0u1/
          http://ow2ct2f1u2/
          http://ow3ot1b2u1/
          http://ow3ot1b1u2/
          http://ow3ot1s0u3/
          http://ow3ot2b1u1/
          http://ow3ot2s0u2/
          http://ow3ot2f1u3/
          http://ow3ot3s0u1/
          http://ow3ot3f1u2/
          http://ow3ot3f2u3/
          http://ow3ct1b1u1/
          http://ow3ct1s0u2/
          http://ow3ct2s0u1/
          http://ow3ct2f1u2/
          http://cw1ot1b1u1/
          http://cw1ot1s0u2/
          http://cw1ot2s0u1/
          http://cw1ot2f1u2/
          http://cw1ct1b1u1/
          http://cw1ct1s0u2/
          http://cw1ct2s0u1/
          http://cw1ct2f1u2/
          http://cw2ot1b1u1/
          http://cw2ot1s0u2/
          http://cw2ot2s0u1/
          http://cw2ot2f1u2/
          http://cw2ct1b1u1/
          http://cw2ct1s0u2/
          http://cw2ct2s0u1/
          http://cw2ct2f1u2/
          '''))
    self.assertEqual(exitstatus, 0)
