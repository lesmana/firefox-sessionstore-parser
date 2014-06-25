
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
    opts = []
    optnames = {}
    optsdict = argvparser.dictifyopts(opts, optnames)
    self.assertEqual(optsdict, {})

  def test_noarg(self):
    argvparser = p.ArgvParser(None, None, None)
    opts = [('-f', '')]
    optnames = {'-f': 'foo'}
    optsdict = argvparser.dictifyopts(opts, optnames)
    self.assertEqual(optsdict, {'foo': ''})

  def test_yesarg(self):
    argvparser = p.ArgvParser(None, None, None)
    opts = [('-f', 'whatfoo')]
    optnames = {'-f': 'foo'}
    optsdict = argvparser.dictifyopts(opts, optnames)
    self.assertEqual(optsdict, {'foo': 'whatfoo'})

class TestSplitOpts(unittest.TestCase):

  #pylint: disable=unused-argument

  def test_empty(self):
    def fakegetopt(argv, shortopts, longopts):
      return [], ['args']
    optionsdata = []
    argvparser = p.ArgvParser(fakegetopt, optionsdata, None)
    argvoptsargs = ['ignored']
    optsdict, argvargs = argvparser.splitopts(argvoptsargs)
    self.assertEqual(optsdict, {})
    self.assertEqual(argvargs, ['args'])

  def test_someopts(self):
    def fakegetopt(argv, shortopts, longopts):
      return [('--opt', 'optarg')], ['args']
    optionsdata = [('optname', ['--opt'], 1)]
    argvparser = p.ArgvParser(fakegetopt, optionsdata, None)
    argvoptsargs = ['ignored']
    optsdict, argvargs = argvparser.splitopts(argvoptsargs)
    self.assertEqual(optsdict, {'optname': 'optarg'})
    self.assertEqual(argvargs, ['args'])

  def test_noopts(self):
    def fakegetopt(argv, shortopts, longopts):
      return [], ['args']
    optionsdata = [('optname', ['--opt'], 1)]
    argvparser = p.ArgvParser(fakegetopt, optionsdata, None)
    argvoptsargs = ['ignored']
    optsdict, argvargs = argvparser.splitopts(argvoptsargs)
    self.assertEqual(optsdict, {})
    self.assertEqual(argvargs, ['args'])

class TestSplitArgs(unittest.TestCase):

  def test_empty(self):
    argumentsdata = []
    argvparser = p.ArgvParser(None, None, argumentsdata)
    argvargs = []
    argsdict, argvrest = argvparser.splitargs(argvargs)
    self.assertEqual(argsdict, {})
    self.assertEqual(argvrest, [])

  def test_someargs(self):
    argumentsdata = ['foo', 'bar']
    argvparser = p.ArgvParser(None, None, argumentsdata)
    argvargs = ['argfoo', 'argbar', 'rest']
    argsdict, argvrest = argvparser.splitargs(argvargs)
    self.assertEqual(argsdict, {
          'foo': 'argfoo',
          'bar': 'argbar'})
    self.assertEqual(argvrest, ['rest'])

  def test_noargs(self):
    argumentsdata = ['foo', 'bar']
    argvparser = p.ArgvParser(None, None, argumentsdata)
    argvargs = []
    argsdict, argvrest = argvparser.splitargs(argvargs)
    self.assertEqual(argsdict, {})
    self.assertEqual(argvrest, [])

class TestParse(unittest.TestCase):

  def test_getopterror(self):
    def fakegetopt(argv, shortopts, longopts):
      #pylint: disable=unused-argument
      raise getopt.GetoptError('bla option bla bla')
    optionsdata = []
    argvparser = p.ArgvParser(fakegetopt, optionsdata, None)
    argv = ['ignored']
    parsedargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {'unknown': ['option']})

  def test_someargs(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argumentsdata = ['filename']
    argvparser = p.ArgvParser(getopt.getopt, optionsdata, argumentsdata)
    argv = ['progname', '--bar', '--foo', 'somefoo', 'filename', 'rest']
    parsedargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {
          'progname': 'progname',
          'bar': '',
          'foo': 'somefoo',
          'filename': 'filename',
          'unknown': ['rest']})
