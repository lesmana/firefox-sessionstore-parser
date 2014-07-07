
import unittest

import contextlib
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
    fakefile = contextlib.closing(StringIO.StringIO(fakefilecontent))
    def fakeopen(dummy_filename):
      return fakefile
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
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), p.SHORTHELP)
    self.assertEqual(exitstatus, 0)

  def test_help(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '-h']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, None)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), p.HELP)
    self.assertEqual(exitstatus, 0)

  def test_version(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--version']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, None)
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(fakestdout.getvalue(), p.VERSION + '\n')
    self.assertEqual(exitstatus, 0)

  def test_nofilename(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--all']
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

  def test_wrongargv2(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--window=wrong', 'irrelevantfilename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, None)
    self.assertEqual(fakestderr.getvalue(),
          'illegal value for "window": "wrong"\n')
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(exitstatus, 2)

  def test_notfile(self):
    def fakeopen(dummy_filename):
      raise IOError('ignored error message')
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'wrongfilename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot open file wrongfilename.\n')
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(exitstatus, 1)

  def test_notjson(self):
    fakefilecontent = textwrap.dedent('''\
          what is this i don't even''')
    fakefile = contextlib.closing(StringIO.StringIO(fakefilecontent))
    def fakeopen(dummy_filename):
      return fakefile
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeargv, fakestdout, fakestderr, fakeopen)
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot read session store from file filename.\n')
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(exitstatus, 1)
