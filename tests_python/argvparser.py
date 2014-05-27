
import unittest

import getopt

import sessionstoreparser as p

class TestSplitOpts(unittest.TestCase):

  def test_noerror(self):
    report = []
    def fakegetopt(argv, shortopts, longopts):
      report.append(('fakegetopt', argv, shortopts, longopts))
      return [('--opt', 'optarg')], ['args']
    optionsdata = {
          'shortopts': '',
          'longopts': [],
          'optnames': {}}
    argvparser = p.ArgvParser(fakegetopt, optionsdata)
    opts, argvargs = argvparser.splitopts('argvoptsargs')
    self.assertEqual(opts, [('--opt', 'optarg')])
    self.assertEqual(argvargs, ['args'])
    self.assertEqual(report, [
          ('fakegetopt', 'argvoptsargs', '', [])])

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
    optionsdata = {
          'shortopts': '',
          'longopts': [],
          'optnames': {}}
    argvparser = p.ArgvParser(fakegetopt, optionsdata)
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
    optionsdata = {
          'shortopts': shortopts,
          'longopts': longopts,
          'optnames': optnames}
    argvparser = p.ArgvParser(getopt.getopt, optionsdata)
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
    optionsdata = {
          'shortopts': shortopts,
          'longopts': longopts,
          'optnames': optnames}
    argvparser = p.ArgvParser(getopt.getopt, optionsdata)
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
    optionsdata = {
          'shortopts': shortopts,
          'longopts': longopts,
          'optnames': optnames}
    argvparser = p.ArgvParser(getopt.getopt, optionsdata)
    options, argvunknown = argvparser.parse(['progname', '--bar', '--foo', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'foo': 'somefoo',
          'filename': 'filename'})
    self.assertEqual(argvunknown, [])
