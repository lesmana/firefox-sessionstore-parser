
import unittest

import getopt

import sessionstoreparser as p

class TestPrepareOptionsData(unittest.TestCase):

  def test_empty(self):
    optionsdata = []
    argvparser = p.ArgvParser(None, None)
    shortopts, longopts, optnames = argvparser.prepareoptionsdata(optionsdata)
    self.assertEqual(shortopts, '')
    self.assertEqual(longopts, [])
    self.assertEqual(optnames, {})

  def test_someoptions(self):
    optionsdata = [
          ('foo', ['-f', '--foo'], 0),
          ('bar', ['-b', '--bar'], 1),
          ('help', ['-h', '--help'], 0)]
    argvparser = p.ArgvParser(None, None)
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
    argvparser = p.ArgvParser(None, None)
    opts = []
    optnames = {}
    optsdict = argvparser.dictifyopts(opts, optnames)
    self.assertEqual(optsdict, {})

  def test_noarg(self):
    argvparser = p.ArgvParser(None, None)
    opts = [('-f', '')]
    optnames = {'-f': 'foo'}
    optsdict = argvparser.dictifyopts(opts, optnames)
    self.assertEqual(optsdict, {'foo': ''})

  def test_yesarg(self):
    argvparser = p.ArgvParser(None, None)
    opts = [('-f', 'whatfoo')]
    optnames = {'-f': 'foo'}
    optsdict = argvparser.dictifyopts(opts, optnames)
    self.assertEqual(optsdict, {'foo': 'whatfoo'})

class TestSplitOpts(unittest.TestCase):

  #pylint: disable=unused-argument

  def test_empty(self):
    optionsdata = []
    argvparser = p.ArgvParser(optionsdata, None)
    argv = []
    optsdict, args = argvparser.splitopts(argv)
    self.assertEqual(optsdict, {})
    self.assertEqual(args, [])

  def test_someopts(self):
    optionsdata = [('optname', ['--opt'], 1)]
    argvparser = p.ArgvParser(optionsdata, None)
    argv = ['--opt', 'optarg', 'args']
    optsdict, args = argvparser.splitopts(argv)
    self.assertEqual(optsdict, {'optname': 'optarg'})
    self.assertEqual(args, ['args'])

  def test_noopts(self):
    optionsdata = [('optname', ['--opt'], 1)]
    argvparser = p.ArgvParser(optionsdata, None)
    argv = ['args']
    optsdict, args = argvparser.splitopts(argv)
    self.assertEqual(optsdict, {})
    self.assertEqual(args, ['args'])

class TestSplitArgs(unittest.TestCase):

  def test_empty(self):
    argumentsdata = []
    argvparser = p.ArgvParser(None, argumentsdata)
    args = []
    argsdict, restargv = argvparser.splitargs(args)
    self.assertEqual(argsdict, {})
    self.assertEqual(restargv, [])

  def test_someargs(self):
    argumentsdata = ['foo', 'bar']
    argvparser = p.ArgvParser(None, argumentsdata)
    args = ['argfoo', 'argbar', 'rest1', 'rest2']
    argsdict, restargv = argvparser.splitargs(args)
    self.assertEqual(argsdict, {
          'foo': 'argfoo',
          'bar': 'argbar'})
    self.assertEqual(restargv, ['rest1', 'rest2'])

  def test_noargs(self):
    argumentsdata = ['foo', 'bar']
    argvparser = p.ArgvParser(None, argumentsdata)
    args = []
    argsdict, restargv = argvparser.splitargs(args)
    self.assertEqual(argsdict, {})
    self.assertEqual(restargv, [])

class TestParse(unittest.TestCase):

  def test_empty(self):
    optionsdata = []
    argumentsdata = []
    argvparser = p.ArgvParser(optionsdata, argumentsdata)
    argv = []
    parsedargv, restargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {})
    self.assertEqual(restargv, [])

  def test_getopterror(self):
    optionsdata = []
    argumentsdata = []
    argvparser = p.ArgvParser(optionsdata, argumentsdata)
    argv = ['--option']
    parsedargv, restargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {})
    self.assertEqual(restargv, ['--option'])

  def test_someargs(self):
    optionsdata = [
          ('help', ['-h', '--help'], 0),
          ('foo', ['-f', '--foo'], 1),
          ('bar', ['-b', '--bar'], 0)]
    argumentsdata = ['filename']
    argvparser = p.ArgvParser(optionsdata, argumentsdata)
    argv = ['--bar', '--foo', 'somefoo', 'filename', 'rest1', 'rest2']
    parsedargv, restargv = argvparser.parse(argv)
    self.assertEqual(parsedargv, {
          'bar': '',
          'foo': 'somefoo',
          'filename': 'filename'})
    self.assertEqual(restargv, ['rest1', 'rest2'])
