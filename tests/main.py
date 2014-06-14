
import unittest

import contextlib
import json
import StringIO
import textwrap
import yaml

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_yamlequaljson(self):
    # verify that objects from json and yaml are equivalent
    yamlstr = textwrap.dedent('''\
          windows:
            - tabs:
                - entries:
                    - url: http://window1tab1url1
                  index: 1
              selected: 1
              _closedTabs: []
          selectedWindow: 0
          _closedWindows: []
          ''')
    jsonstr = textwrap.dedent('''\
          {
            "windows": [{
              "tabs": [{
                "entries": [{
                  "url": "http://window1tab1url1"}],
                "index": 1}],
              "selected": 1,
              "_closedTabs": []}],
            "selectedWindow": 0,
            "_closedWindows": []}
          ''')
    yamlobj = yaml.load(yamlstr)
    jsonobj = json.loads(jsonstr)
    jsonstrfromyamlobj = json.dumps(yamlobj)
    jsonstrfromjsonobj = json.dumps(jsonobj)
    self.assertEqual(jsonstrfromyamlobj, jsonstrfromjsonobj)

  def test_default(self):
    fakefilecontent = json.dumps(yaml.load(textwrap.dedent('''\
          windows:
            - tabs:
                - entries:
                    - url: http://window1tab1url1
                  index: 1
              selected: 1
              _closedTabs: []
          selectedWindow: 0
          _closedWindows: []
          ''')))
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), 'http://window1tab1url1\n')
    self.assertEqual(fakestderr.getvalue(), '')

  def test_noargv(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname']
    exitstatus = p.secludedmain(None, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 2)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'missing argument: filename\n')

  def test_wrongargv(self):
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', '--wrong']
    exitstatus = p.secludedmain(None, fakestdout, fakestderr, fakeargv)
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
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
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
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 1)
    self.assertEqual(fakestdout.getvalue(), '')
    self.assertEqual(fakestderr.getvalue(),
          'error: cannot read session store from file filename.\n')

  def test_threetabs(self):
    fakefilecontent = json.dumps(yaml.load(textwrap.dedent('''\
          windows:
            - tabs:
                - entries:
                    - url: http://window1tab1url1
                  index: 1
                - entries:
                    - url: http://window1tab2url1
                  index: 1
                - entries:
                    - url: http://window1tab3url1
                  index: 1
              selected: 3
              _closedTabs: []
          selectedWindow: 0
          _closedWindows: []
          ''')))
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://window1tab1url1
          http://window1tab2url1
          http://window1tab3url1
          '''))
    self.assertEqual(fakestderr.getvalue(), '')

  def test_twowindows(self):
    fakefilecontent = json.dumps(yaml.load(textwrap.dedent('''\
          windows:
            - tabs:
                - entries:
                    - url: http://window1tab1url1
                  index: 1
              selected: 1
              _closedTabs: []
            - tabs:
                - entries:
                    - url: http://window2tab1url1
                  index: 1
              selected: 1
              _closedTabs: []
          selectedWindow: 2
          _closedWindows: []
          ''')))
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://window1tab1url1
          http://window2tab1url1
          '''))
    self.assertEqual(fakestderr.getvalue(), '')

  def test_history(self):
    fakefilecontent = json.dumps(yaml.load(textwrap.dedent('''\
          windows:
            - tabs:
                - entries:
                    - url: http://window1tab1url1
                    - url: http://window1tab1url2
                    - url: http://window1tab1url3
                  index: 3
              selected: 1
              _closedTabs: []
          selectedWindow: 0
          _closedWindows: []
          ''')))
    fakefile = StringIO.StringIO(fakefilecontent)
    def fakeopen(dummy_filename):
      return contextlib.closing(fakefile)
    fakestdout = StringIO.StringIO()
    fakestderr = StringIO.StringIO()
    fakeargv = ['progname', 'filename']
    exitstatus = p.secludedmain(fakeopen, fakestdout, fakestderr, fakeargv)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(fakestdout.getvalue(), textwrap.dedent('''\
          http://window1tab1url3
          '''))
    self.assertEqual(fakestderr.getvalue(), '')
