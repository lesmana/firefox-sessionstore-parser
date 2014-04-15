
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

  def test_filename(self):
    argvhandler = p.ArgvHandler()
    options = argvhandler.handle(['progname', 'filename'])
    self.assertEqual(options, {'filename': 'filename'})

  def test_nofilename(self):
    argvhandler = p.ArgvHandler()
    try:
      _ = argvhandler.handle(['progname'])
    except p.ArgvError as err:
      self.assertEqual(str(err), 'need filename')
    else:
      self.fail('expected exception') # pragma: no cover
