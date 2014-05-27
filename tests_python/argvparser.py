
import unittest

import getopt

import sessionstoreparser as p

class TestSplitOpts(unittest.TestCase):

  def test_noerror(self):
    report = []
    def fakegetopt(argv, shortopts, longopts):
      report.append(('fakegetopt', argv, shortopts, longopts))
      return [('optname', 'optarg')], ['args']
    argvparser = p.ArgvParser(fakegetopt, '', [], {})
    opts, argvargs = argvparser.splitopts('argvoptsargs')
    self.assertEqual(opts, [('optname', 'optarg')])
    self.assertEqual(argvargs, ['args'])
    self.assertEqual(report, [
          ('fakegetopt', 'argvoptsargs', '', [])])

class TestDictifyOpts(unittest.TestCase):

  def test_empty(self):
    argvparser = p.ArgvParser(None, None, None, {})
    optsdict = argvparser.dictifyopts([], {})
    self.assertEqual(optsdict, {})

  def test_trueifemptyval(self):
    argvparser = p.ArgvParser(None, None, None, {'-f': 'foo'})
    optsdict = argvparser.dictifyopts([('-f', '')], {'-f': 'foo'})
    self.assertEqual(optsdict, {'foo': True})

  def test_valifnotemptyval(self):
    argvparser = p.ArgvParser(None, None, None, {'-f': 'foo'})
    optsdict = argvparser.dictifyopts([('-f', 'whatfoo')], {'-f': 'foo'})
    self.assertEqual(optsdict, {'foo': 'whatfoo'})

class TestParse(unittest.TestCase):

  def test_getopterror(self):
    def fakegetopt(argv, shortopts, longopts):
      raise getopt.GetoptError('silly error')
    argvparser = p.ArgvParser(fakegetopt, '', [], {})
    options, argvunknown = argvparser.parse('argv')
    self.assertEqual(options, {})
    self.assertEqual(argvunknown, ['silly error'])

  def test_foo(self):
    shortopts = 'hf:b'
    longopts = ['help', 'foo=', 'bar']
    optnames = {
          '-h': 'help',
          '--help': 'help',
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar'}
    argvparser = p.ArgvParser(getopt.getopt, shortopts, longopts, optnames)
    options, argvunknown = argvparser.parse(['progname', '-f', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'foo': 'somefoo',
          'filename': 'filename'})
    self.assertEqual(argvunknown, [])

  def test_bar(self):
    shortopts = 'hf:b'
    longopts = ['help', 'foo=', 'bar']
    optnames = {
          '-h': 'help',
          '--help': 'help',
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar'}
    argvparser = p.ArgvParser(getopt.getopt, shortopts, longopts, optnames)
    options, argvunknown = argvparser.parse(['progname', '--bar', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'filename': 'filename'})
    self.assertEqual(argvunknown, [])

  def test_foobar(self):
    shortopts = 'hf:b'
    longopts = ['help', 'foo=', 'bar']
    optnames = {
          '-h': 'help',
          '--help': 'help',
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar'}
    argvparser = p.ArgvParser(getopt.getopt, shortopts, longopts, optnames)
    options, argvunknown = argvparser.parse(['progname', '--bar', '--foo', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'foo': 'somefoo',
          'filename': 'filename'})
    self.assertEqual(argvunknown, [])
