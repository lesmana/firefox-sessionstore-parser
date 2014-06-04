
import unittest

import getopt

import sessionstoreparser as p

class TestPrepareOptionsData(unittest.TestCase):

  def test_empty(self):
    optionsdata = []
    argvparser = p.ArgvParser(None, None, None)
    shortopts, longopts, optnames = argvparser.prepareoptionsdata(optionsdata)
    self.assertEqual(shortopts, '')
    self.assertEqual(longopts, [])
    self.assertEqual(optnames, {})

  def test_someoptions(self):
    optionsdata = [
          ('foo', ['-f', '--foo'], 0),
          ('bar', ['-b', '--bar'], 1),
          ('help', ['-h', '--help'], 0)]
    argvparser = p.ArgvParser(None, None, None)
    shortopts, longopts, optnames = argvparser.prepareoptionsdata(optionsdata)
    self.assertEqual(shortopts, 'fb:h')
    self.assertEqual(longopts, ['foo', 'bar=', 'help'])
    self.assertEqual(optnames, {
          '-f': 'foo',
          '--foo': 'foo',
          '-b': 'bar',
          '--bar': 'bar',
          '-h': 'help',
          '--help': 'help'})

class TestDictifyOpts(unittest.TestCase):

  def test_empty(self):
    argvparser = p.ArgvParser(None, None, None)
    optsdict = argvparser.dictifyopts([], {})
    self.assertEqual(optsdict, {})

  def test_trueifemptyval(self):
    argvparser = p.ArgvParser(None, None, None)
    optsdict = argvparser.dictifyopts([('-f', '')], {'-f': 'foo'})
    self.assertEqual(optsdict, {'foo': ''})

  def test_valifnotemptyval(self):
    argvparser = p.ArgvParser(None, None, None)
    optsdict = argvparser.dictifyopts([('-f', 'whatfoo')], {'-f': 'foo'})
    self.assertEqual(optsdict, {'foo': 'whatfoo'})

class TestSplitOpts(unittest.TestCase):

  def test_noerror(self):
    def fakegetopt(argv, shortopts, longopts):
      #pylint: disable=unused-argument
      return [('--opt', 'optarg')], ['args']
    optionsdata = [
          ('optname', ['--opt'], 1)]
    argvparser = p.ArgvParser(fakegetopt, optionsdata, None)
    optsdict, argvargs = argvparser.splitopts('argvoptsargs')
    self.assertEqual(optsdict, {
          'optname': 'optarg'})
    self.assertEqual(argvargs, ['args'])

class TestSplitArgs(unittest.TestCase):

  def test_empty(self):
    argumentsdata = []
    argvparser = p.ArgvParser(None, None, argumentsdata)
    argsdict, argvrest = argvparser.splitargs([])
    self.assertEqual(argsdict, {})
    self.assertEqual(argvrest, [])

  def test_someargs(self):
    argumentsdata = ['foo', 'bar']
    argvparser = p.ArgvParser(None, None, argumentsdata)
    argsdict, argvrest = argvparser.splitargs(['argfoo', 'argbar', 'rest'])
    self.assertEqual(argsdict, {
          'foo': 'argfoo',
          'bar': 'argbar'})
    self.assertEqual(argvrest, ['rest'])

  def test_noargs(self):
    argumentsdata = ['foo', 'bar']
    argvparser = p.ArgvParser(None, None, argumentsdata)
    argsdict, argvrest = argvparser.splitargs([])
    self.assertEqual(argsdict, {})
    self.assertEqual(argvrest, [])

class TestParse(unittest.TestCase):

  def test_getopterror(self):
    def fakegetopt(argv, shortopts, longopts):
      #pylint: disable=unused-argument
      raise getopt.GetoptError('bla option bla bla')
    optionsdata = []
    argvparser = p.ArgvParser(fakegetopt, optionsdata, None)
    parsedargv = argvparser.parse('argv')
    self.assertEqual(parsedargv, {'unknown': ['option']})

  def test_foo(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argumentsdata = ['filename']
    argvparser = p.ArgvParser(getopt.getopt, optionsdata, argumentsdata)
    argv = ['progname', '-f', 'somefoo', 'filename']
    parsedargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {
          'progname': 'progname',
          'foo': 'somefoo',
          'filename': 'filename'})

  def test_bar(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argumentsdata = ['filename']
    argvparser = p.ArgvParser(getopt.getopt, optionsdata, argumentsdata)
    argv = ['progname', '--bar', 'filename']
    parsedargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {
          'progname': 'progname',
          'bar': '',
          'filename': 'filename'})

  def test_foobar(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argumentsdata = ['filename']
    argvparser = p.ArgvParser(getopt.getopt, optionsdata, argumentsdata)
    argv = ['progname', '--bar', '--foo', 'somefoo', 'filename']
    parsedargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {
          'progname': 'progname',
          'bar': '',
          'foo': 'somefoo',
          'filename': 'filename'})
