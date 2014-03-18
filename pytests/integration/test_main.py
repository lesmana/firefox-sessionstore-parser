
import unittest

import contextlib
import StringIO
import textwrap

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_default(self):
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
      if filename == 'filename':
        return contextlib.closing(fakefile)
      else:
        self.fail('unexpected filename: ' + filename)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), 'http://window1tab1url1\n')
    self.assertEqual(fakestderr.getvalue(), '')
