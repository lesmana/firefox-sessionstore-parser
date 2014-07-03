
import unittest

import contextlib
import os
import StringIO
import textwrap

import sessionstoreparser as p

def gettestdata():
  filename = os.path.join(os.path.dirname(__file__), 'testdata.js')
  with open(filename) as testdatafile:
    testdata = testdatafile.read()
  return testdata

class TestMainRealData(unittest.TestCase):

  testdata = gettestdata()

  def test_default(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://sw1-ot1-s0u3/
          http://sw1-ot2-s0u2/
          http://sw1-st3-s0u1/
          http://ow2-ot1-s0u3/
          http://ow2-st2-s0u2/
          http://ow2-ot3-s0u1/
          http://ow3-st1-s0u3/
          http://ow3-ot2-s0u2/
          http://ow3-ot3-s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_all(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--all', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://sw1-ot1-s0u3/
          http://sw1-ot2-s0u2/
          http://sw1-st3-s0u1/
          http://sw1-ct1-s0u2/
          http://sw1-ct2-s0u1/
          http://ow2-ot1-s0u3/
          http://ow2-st2-s0u2/
          http://ow2-ot3-s0u1/
          http://ow2-ct1-s0u2/
          http://ow2-ct2-s0u1/
          http://ow3-st1-s0u3/
          http://ow3-ot2-s0u2/
          http://ow3-ot3-s0u1/
          http://ow3-ct1-s0u2/
          http://ow3-ct2-s0u1/
          http://cw1-ot1-s0u2/
          http://cw1-st2-s0u1/
          http://cw1-ct1-s0u2/
          http://cw1-ct2-s0u1/
          http://cw2-st1-s0u2/
          http://cw2-ot2-s0u1/
          http://cw2-ct1-s0u2/
          http://cw2-ct2-s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_allwithhistory(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--all-with-history', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://sw1-ot1-b2u1/
          http://sw1-ot1-b1u2/
          http://sw1-ot1-s0u3/
          http://sw1-ot2-b1u1/
          http://sw1-ot2-s0u2/
          http://sw1-ot2-f1u3/
          http://sw1-st3-s0u1/
          http://sw1-st3-f1u2/
          http://sw1-st3-f2u3/
          http://sw1-ct1-b1u1/
          http://sw1-ct1-s0u2/
          http://sw1-ct2-s0u1/
          http://sw1-ct2-f1u2/
          http://ow2-ot1-b2u1/
          http://ow2-ot1-b1u2/
          http://ow2-ot1-s0u3/
          http://ow2-st2-b1u1/
          http://ow2-st2-s0u2/
          http://ow2-st2-f1u3/
          http://ow2-ot3-s0u1/
          http://ow2-ot3-f1u2/
          http://ow2-ot3-f2u3/
          http://ow2-ct1-b1u1/
          http://ow2-ct1-s0u2/
          http://ow2-ct2-s0u1/
          http://ow2-ct2-f1u2/
          http://ow3-st1-b2u1/
          http://ow3-st1-b1u2/
          http://ow3-st1-s0u3/
          http://ow3-ot2-b1u1/
          http://ow3-ot2-s0u2/
          http://ow3-ot2-f1u3/
          http://ow3-ot3-s0u1/
          http://ow3-ot3-f1u2/
          http://ow3-ot3-f2u3/
          http://ow3-ct1-b1u1/
          http://ow3-ct1-s0u2/
          http://ow3-ct2-s0u1/
          http://ow3-ct2-f1u2/
          http://cw1-ot1-b1u1/
          http://cw1-ot1-s0u2/
          http://cw1-st2-s0u1/
          http://cw1-st2-f1u2/
          http://cw1-ct1-b1u1/
          http://cw1-ct1-s0u2/
          http://cw1-ct2-s0u1/
          http://cw1-ct2-f1u2/
          http://cw2-st1-b1u1/
          http://cw2-st1-s0u2/
          http://cw2-ot2-s0u1/
          http://cw2-ot2-f1u2/
          http://cw2-ct1-b1u1/
          http://cw2-ct1-s0u2/
          http://cw2-ct2-s0u1/
          http://cw2-ct2-f1u2/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_windowclosed(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--window=closed', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://cw1-ot1-s0u2/
          http://cw1-st2-s0u1/
          http://cw2-st1-s0u2/
          http://cw2-ot2-s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_tabclosed(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--tab=closed', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://sw1-ct1-s0u2/
          http://sw1-ct2-s0u1/
          http://ow2-ct1-s0u2/
          http://ow2-ct2-s0u1/
          http://ow3-ct1-s0u2/
          http://ow3-ct2-s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_urlall(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--url=all', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://sw1-ot1-b2u1/
          http://sw1-ot1-b1u2/
          http://sw1-ot1-s0u3/
          http://sw1-ot2-b1u1/
          http://sw1-ot2-s0u2/
          http://sw1-ot2-f1u3/
          http://sw1-st3-s0u1/
          http://sw1-st3-f1u2/
          http://sw1-st3-f2u3/
          http://ow2-ot1-b2u1/
          http://ow2-ot1-b1u2/
          http://ow2-ot1-s0u3/
          http://ow2-st2-b1u1/
          http://ow2-st2-s0u2/
          http://ow2-st2-f1u3/
          http://ow2-ot3-s0u1/
          http://ow2-ot3-f1u2/
          http://ow2-ot3-f2u3/
          http://ow3-st1-b2u1/
          http://ow3-st1-b1u2/
          http://ow3-st1-s0u3/
          http://ow3-ot2-b1u1/
          http://ow3-ot2-s0u2/
          http://ow3-ot2-f1u3/
          http://ow3-ot3-s0u1/
          http://ow3-ot3-f1u2/
          http://ow3-ot3-f2u3/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_windowclosed_tabclosed_urlall(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname',
          '--window=closed', '--tab=closed', '--url=all', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://cw1-ct1-b1u1/
          http://cw1-ct1-s0u2/
          http://cw1-ct2-s0u1/
          http://cw1-ct2-f1u2/
          http://cw2-ct1-b1u1/
          http://cw2-ct1-s0u2/
          http://cw2-ct2-s0u1/
          http://cw2-ct2-f1u2/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_selected(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--selected', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://sw1-st3-s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_closed(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--closed', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://cw1-ct1-s0u2/
          http://cw1-ct2-s0u1/
          http://cw2-ct1-s0u2/
          http://cw2-ct2-s0u1/
          '''))
    self.assertEqual(exitstatus, 0)

  def test_closedwithhistory(self):
    fakefile = contextlib.closing(StringIO.StringIO(self.testdata))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--closed-with-history', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://cw1-ct1-b1u1/
          http://cw1-ct1-s0u2/
          http://cw1-ct2-s0u1/
          http://cw1-ct2-f1u2/
          http://cw2-ct1-b1u1/
          http://cw2-ct1-s0u2/
          http://cw2-ct2-s0u1/
          http://cw2-ct2-f1u2/
          '''))
    self.assertEqual(exitstatus, 0)
