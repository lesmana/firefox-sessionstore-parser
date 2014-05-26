
import unittest

import getopt

import sessionstoreparser as p

class TestGetopt(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvParser(object):
      def trygetopt(self, argv1e):
        report.append(('trygetopt', argv1e))
        return 'opts', 'args'
    opts, args = p.ArgvParser.getopt.__func__(FakeArgvParser(), 'argv1e')
    self.assertEqual(opts, 'opts')
    self.assertEqual(args, 'args')
    self.assertEqual(report, [
          ('trygetopt', 'argv1e')])

  def test_error(self):
    report = []
    class FakeArgvParser(object):
      def trygetopt(self, argv1e):
        report.append(('trygetopt', argv1e))
        raise getopt.GetoptError('silly error')
    try:
      _ = p.ArgvParser.getopt.__func__(FakeArgvParser(), 'argv1e')
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

  def test_noerror(self):
    report = []
    class FakeArgvParser(object):
      def splitprogname(self, argv):
        report.append(('splitprogname', argv))
        return 'progname', 'argv1e'
      def getopt(self, argv1e):
        report.append(('getopt', argv1e))
        return 'opts', 'args'
      def dictify(self, opts, args):
        report.append(('dictify', opts, args))
        return 'options'
    options = p.ArgvParser.parse.__func__(FakeArgvParser(), 'argv')
    self.assertEqual(options, 'options')
    self.assertEqual(report, [
          ('splitprogname', 'argv'),
          ('getopt', 'argv1e'),
          ('dictify', 'opts', 'args')])

  def test_getopterror(self):
    report = []
    def fakegetopt(argv, shortopts, longopts):
      report.append(('splitprogname', 'argv'))
      report.append(('getopt', 'argv1e'))
      raise p.ArgvError('silly error')
    argvparser = p.ArgvParser(fakegetopt, '', [], {})
    try:
      _ = argvparser.parse('argv')
    except p.ArgvError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('splitprogname', 'argv'),
          ('getopt', 'argv1e')])

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
