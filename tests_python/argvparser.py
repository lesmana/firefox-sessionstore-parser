
import unittest

import getopt

import sessionstoreparser as p

class TestSplitOptionsData(unittest.TestCase):

  def test_empty(self):
    optionsdata = []
    argvparser = p.ArgvParser(None, None)
    shortopts, longopts, optnames = argvparser.splitoptionsdata(optionsdata)
    self.assertEqual(shortopts, '')
    self.assertEqual(longopts, [])
    self.assertEqual(optnames, {})

  def test_someoptions(self):
    optionsdata = [
          ('foo', ['-f', '--foo'], 0),
          ('bar', ['-b', '--bar'], 1),
          ('help', ['-h', '--help'], 0)]
    argvparser = p.ArgvParser(None, None)
    shortopts, longopts, optnames = argvparser.splitoptionsdata(optionsdata)
    self.assertEqual(shortopts, 'fb:h')
    self.assertEqual(longopts, ['foo', 'bar=', 'help'])
    self.assertEqual(optnames, {
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar',
          '-h': 'help',
          '--help': 'help'})

class TestSplitOpts(unittest.TestCase):

  def test_noerror(self):
    def fakegetopt(argv, shortopts, longopts):
      return [('--opt', 'optarg')], ['args']
    optionsdata = []
    argvparser = p.ArgvParser(fakegetopt, optionsdata)
    opts, argvargs = argvparser.splitopts('argvoptsargs')
    self.assertEqual(opts, [('--opt', 'optarg')])
    self.assertEqual(argvargs, ['args'])

class TestDictifyOpts(unittest.TestCase):

  def test_empty(self):
    argvparser = p.ArgvParser(None, None)
    optsdict = argvparser.dictifyopts([], {})
    self.assertEqual(optsdict, {})

  def test_trueifemptyval(self):
    argvparser = p.ArgvParser(None, None)
    optsdict = argvparser.dictifyopts([('-f', '')], {'-f': 'foo'})
    self.assertEqual(optsdict, {'foo': True})

  def test_valifnotemptyval(self):
    argvparser = p.ArgvParser(None, None)
    optsdict = argvparser.dictifyopts([('-f', 'whatfoo')], {'-f': 'foo'})
    self.assertEqual(optsdict, {'foo': 'whatfoo'})

class TestParse(unittest.TestCase):

  def test_getopterror(self):
    def fakegetopt(argv, shortopts, longopts):
      raise getopt.GetoptError('silly error')
    optionsdata = []
    argvparser = p.ArgvParser(fakegetopt, optionsdata)
    options, argvunknown = argvparser.parse('argv')
    self.assertEqual(options, {})
    self.assertEqual(argvunknown, ['silly error'])

  def test_foo(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argvparser = p.ArgvParser(getopt.getopt, optionsdata)
    options, argvunknown = argvparser.parse(['progname', '-f', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'foo': 'somefoo',
          'filename': 'filename'})
    self.assertEqual(argvunknown, [])

  def test_bar(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argvparser = p.ArgvParser(getopt.getopt, optionsdata)
    options, argvunknown = argvparser.parse(['progname', '--bar', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'filename': 'filename'})
    self.assertEqual(argvunknown, [])

  def test_foobar(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argvparser = p.ArgvParser(getopt.getopt, optionsdata)
    options, argvunknown = argvparser.parse(['progname', '--bar', '--foo', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'foo': 'somefoo',
          'filename': 'filename'})
    self.assertEqual(argvunknown, [])
