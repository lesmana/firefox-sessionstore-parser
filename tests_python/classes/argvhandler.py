
import unittest

import sessionstoreparser as p

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
