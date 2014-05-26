
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

class TestCreateWorker(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeWorker(object):
      def __init__(self, sessionstoreparser):
        self.sessionstoreparser = sessionstoreparser
    class FakeWorkerFactory(object):
      def produce(self, options):
        report.append(('produce', options))
        return FakeWorker('parser')
    app = p.Application(None, FakeWorkerFactory())
    worker = app.createworker('options')
    self.assertEqual(worker.sessionstoreparser, 'parser')
    self.assertEqual(report, [
          ('produce', 'options')])

class TestDoWork(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeSessionStoreParserWorker(object):
      def work(self):
        report.append(('work', 'options'))
        return 0
    app = p.Application(None, None)
    exitstatus = app.dowork(FakeSessionStoreParserWorker())
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
        report.append(('createworker', options))
        return 'worker'
      def dowork(self, options):
        report.append(('dowork', 'worker'))
        return 'exitstatus'
    fakeapp = FakeApplication()
    exitstatus = p.Application.tryrun.__func__(fakeapp, 'argv')
    self.assertEqual(exitstatus, 'exitstatus')
    self.assertEqual(report, [
          ('handleargv', 'argv'),
          ('createworker', 'options'),
          ('dowork', 'worker')])

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
