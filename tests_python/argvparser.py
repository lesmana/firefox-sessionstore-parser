
import unittest

import getopt

import sessionstoreparser as p

class TestGetopt(unittest.TestCase):

  def test_noerror(self):
    report = []
    def fakegetopt(argv, shortopts, longopts):
      report.append(('trygetopt', 'argv1e'))
      return 'opts', 'args'
    argvparser = p.ArgvParser(fakegetopt, '', [], {})
    opts, args = argvparser.getopt('argv1e')
    self.assertEqual(opts, 'opts')
    self.assertEqual(args, 'args')
    self.assertEqual(report, [
          ('trygetopt', 'argv1e')])

  def test_error(self):
    report = []
    def fakegetopt(argv, shortopts, longopts):
      report.append(('trygetopt', 'argv1e'))
      raise getopt.GetoptError('silly error')
    argvparser = p.ArgvParser(fakegetopt, '', [], {})
    try:
      _ = argvparser.getopt('argv1e')
    except p.ArgvError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('trygetopt', 'argv1e')])

class TestDictifyOpts(unittest.TestCase):

  def test_empty(self):
    argvparser = p.ArgvParser(None, None, None, {})
    optsdict = argvparser.dictifyopts([])
    self.assertEqual(optsdict, {})

  def test_trueifemptyval(self):
    argvparser = p.ArgvParser(None, None, None, {'-f': 'foo'})
    optsdict = argvparser.dictifyopts([('-f', '')])
    self.assertEqual(optsdict, {'foo': True})

  def test_valifnotemptyval(self):
    argvparser = p.ArgvParser(None, None, None, {'-f': 'foo'})
    optsdict = argvparser.dictifyopts([('-f', 'whatfoo')])
    self.assertEqual(optsdict, {'foo': 'whatfoo'})

class TestParse(unittest.TestCase):

  def test_getopterror(self):
    def fakegetopt(argv, shortopts, longopts):
      raise p.ArgvError('silly error')
    argvparser = p.ArgvParser(fakegetopt, '', [], {})
    try:
      _ = argvparser.parse('argv')
    except p.ArgvError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover

  def test_foo(self):
    shortopts = 'hf:b'
    longopts = ['help', 'foo=', 'bar']
    optnametable = {
          '-h': 'help',
          '--help': 'help',
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar'}
    argvparser = p.ArgvParser(getopt.getopt, shortopts, longopts, optnametable)
    options = argvparser.parse(['progname', '-f', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'foo': 'somefoo',
          'filename': 'filename'})

  def test_bar(self):
    shortopts = 'hf:b'
    longopts = ['help', 'foo=', 'bar']
    optnametable = {
          '-h': 'help',
          '--help': 'help',
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar'}
    argvparser = p.ArgvParser(getopt.getopt, shortopts, longopts, optnametable)
    options = argvparser.parse(['progname', '--bar', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'filename': 'filename'})

  def test_foobar(self):
    shortopts = 'hf:b'
    longopts = ['help', 'foo=', 'bar']
    optnametable = {
          '-h': 'help',
          '--help': 'help',
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar'}
    argvparser = p.ArgvParser(getopt.getopt, shortopts, longopts, optnametable)
    options = argvparser.parse(['progname', '--bar', '--foo', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'foo': 'somefoo',
          'filename': 'filename'})
