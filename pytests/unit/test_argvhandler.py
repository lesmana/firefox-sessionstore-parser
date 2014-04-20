
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
    fakeargvhandler = FakeArgvHandler()
    opts, args = p.ArgvHandler.getopt.__func__(fakeargvhandler, 'argv')
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
    fakeargvhandler = FakeArgvHandler()
    try:
      _ = p.ArgvHandler.getopt.__func__(fakeargvhandler, 'argv')
    except p.ArgvError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('trygetopt', 'argv')])

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
    fakeargvhandler = FakeArgvHandler()
    options = p.ArgvHandler.handle.__func__(fakeargvhandler, 'argv')
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
    fakeargvhandler = FakeArgvHandler()
    try:
      _ = p.ArgvHandler.handle.__func__(fakeargvhandler, 'argv')
    except p.ArgvError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('getopt', 'argv')])
