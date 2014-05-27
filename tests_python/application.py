
import unittest

import StringIO

import sessionstoreparser as p

class TestParseArgv(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvParser(object):
      def parse(self, argv):
        report.append(('parse', argv))
        return 'options', 'argvunknown'
    app = p.Application(FakeArgvParser(), None)
    options, argvunknown = app.parseargv('argv')
    self.assertEqual(options, 'options')
    self.assertEqual(argvunknown, 'argvunknown')
    self.assertEqual(report, [
          ('parse', 'argv')])

class TestCreateWorker(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeWorkerFactory(object):
      def produce(self, options, argvunknown):
        report.append(('produce', options, argvunknown))
        return 'worker'
    app = p.Application(None, FakeWorkerFactory())
    worker = app.createworker('options', 'argvunknown')
    self.assertEqual(worker, 'worker')
    self.assertEqual(report, [
          ('produce', 'options', 'argvunknown')])

class TestDoWork(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeWorker(object):
      def __call__(self):
        report.append(('work', ))
        return 'exitstatus'
    app = p.Application(None, None)
    exitstatus = app.dowork(FakeWorker())
    self.assertEqual(exitstatus, 'exitstatus')
    self.assertEqual(report, [
          ('work', )])

class TestTryRun(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvParser(object):
      def parse(self, argv):
        report.append(('parse', argv))
        return 'options', 'argvunknown'
    class FakeWorkerFactory(object):
      def produce(self, options, argvunknown):
        report.append(('produce', options, argvunknown))
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        report.append(('work', ))
        return 'exitstatus'
    app = p.Application(FakeArgvParser(), FakeWorkerFactory())
    exitstatus = app.tryrun('argv')
    self.assertEqual(exitstatus, 'exitstatus')
    self.assertEqual(report, [
          ('parse', 'argv'),
          ('produce', 'options', 'argvunknown'),
          ('work', )])

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
