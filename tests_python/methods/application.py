
import unittest

import StringIO

import sessionstoreparser as p

class TestHandleArgv(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvHandler(object):
      def handle(self, argv):
        report.append(('handle', argv))
        return 'options'
    app = p.Application(FakeArgvHandler(), None)
    options = app.handleargv(['progname', 'argv'])
    self.assertEqual(options, 'options')
    self.assertEqual(report, [
          ('handle', ['argv'])])

class TestDoWork(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeSessionStoreParser(object):
      def parse(self, options):
        report.append(('work', options))
    app = p.Application(None, FakeSessionStoreParser())
    exitstatus = app.dowork('options')
    self.assertEqual(exitstatus, 0)
    self.assertEqual(report, [
          ('work', 'options')])

class TestTryRun(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeApplication(object):
      def handleargv(self, argv):
        report.append(('handleargv', argv))
        return 'options'
      def createworker(self, options):
        return 'worker'
      def dowork(self, options):
        report.append(('dowork', options))
        return 'exitstatus'
    fakeapp = FakeApplication()
    exitstatus = p.Application.tryrun.__func__(fakeapp, 'argv')
    self.assertEqual(exitstatus, 'exitstatus')
    self.assertEqual(report, [
          ('handleargv', 'argv'),
          ('dowork', 'options')])

class TestRun(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeApplication(object):
      def tryrun(self, argv):
        report.append(('tryrun', argv))
        return 'exitstatus'
    fakeapp = FakeApplication()
    stderr = StringIO.StringIO()
    exitstatus = p.Application.run.__func__(fakeapp, 'argv', stderr)
    self.assertEqual(stderr.getvalue(), '')
    self.assertEqual(exitstatus, 'exitstatus')
    self.assertEqual(report, [
          ('tryrun', 'argv')])

  def test_argverror(self):
    report = []
    class FakeApplication(object):
      def tryrun(self, argv):
        report.append(('tryrun', argv))
        raise p.ArgvError('argv error')
    fakeapp = FakeApplication()
    stderr = StringIO.StringIO()
    exitstatus = p.Application.run.__func__(fakeapp, 'argv', stderr)
    self.assertEqual(stderr.getvalue(), 'argv error\n')
    self.assertEqual(exitstatus, 2)
    self.assertEqual(report, [
          ('tryrun', 'argv')])

  def test_genericerror(self):
    report = []
    class FakeApplication(object):
      def tryrun(self, argv):
        report.append(('tryrun', argv))
        raise p.Error('generic error')
    fakeapp = FakeApplication()
    stderr = StringIO.StringIO()
    exitstatus = p.Application.run.__func__(fakeapp, 'argv', stderr)
    self.assertEqual(stderr.getvalue(), 'generic error\n')
    self.assertEqual(exitstatus, 1)
    self.assertEqual(report, [
          ('tryrun', 'argv')])
