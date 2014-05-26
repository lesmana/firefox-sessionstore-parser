
import unittest

import getopt

import sessionstoreparser as p

class TestGetopt(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvHandler(object):
      def trygetopt(self, argv):
        report.append(('trygetopt', argv))
        return 'opts', 'args'
    opts, args = p.ArgvHandler.getopt.__func__(FakeArgvHandler(), 'argv')
    self.assertEqual(opts, 'opts')
    self.assertEqual(args, 'args')
    self.assertEqual(report, [
          ('trygetopt', 'argv')])

  def test_error(self):
    report = []
    class FakeArgvHandler(object):
      def trygetopt(self, argv):
        report.append(('trygetopt', argv))
        raise getopt.GetoptError('silly error')
    try:
      _ = p.ArgvHandler.getopt.__func__(FakeArgvHandler(), 'argv')
    except p.ArgvError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('trygetopt', 'argv')])

class TestDictifyOpts(unittest.TestCase):

  def test_empty(self):
    argvhandler = p.ArgvHandler(None, None, {})
    optsdict = argvhandler.dictifyopts([])
    self.assertEqual(optsdict, {})

  def test_trueifemptyval(self):
    argvhandler = p.ArgvHandler(None, None, {'-f': 'foo'})
    optsdict = argvhandler.dictifyopts([('-f', '')])
    self.assertEqual(optsdict, {'foo': True})

  def test_valifnotemptyval(self):
    argvhandler = p.ArgvHandler(None, None, {'-f': 'foo'})
    optsdict = argvhandler.dictifyopts([('-f', 'whatfoo')])
    self.assertEqual(optsdict, {'foo': 'whatfoo'})

class TestHandle(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvHandler(object):
      def getopt(self, argv):
        report.append(('getopt', argv))
        return 'opts', 'args'
      def dictify(self, opts, args):
        report.append(('dictify', opts, args))
        return 'options'
    options = p.ArgvHandler.handle.__func__(FakeArgvHandler(), 'argv')
    self.assertEqual(options, 'options')
    self.assertEqual(report, [
          ('getopt', 'argv'),
          ('dictify', 'opts', 'args')])

  def test_getopterror(self):
    report = []
    class FakeArgvHandler(object):
      def getopt(self, argv):
        report.append(('getopt', argv))
        raise p.ArgvError('silly error')
    try:
      _ = p.ArgvHandler.handle.__func__(FakeArgvHandler(), 'argv')
    except p.ArgvError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('getopt', 'argv')])

class TestArgvHandler(unittest.TestCase):

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
    argvhandler = p.ArgvHandler(shortopts, longopts, optnametable)
    options = argvhandler.handle(['-f', 'somefoo', 'filename'])
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
    argvhandler = p.ArgvHandler(shortopts, longopts, optnametable)
    options = argvhandler.handle(['--bar', 'filename'])
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
    argvhandler = p.ArgvHandler(shortopts, longopts, optnametable)
    options = argvhandler.handle(['--bar', '--foo', 'somefoo', 'filename'])
    self.assertEqual(options, {
          'bar': True,
          'foo': 'somefoo',
          'filename': 'filename'})
