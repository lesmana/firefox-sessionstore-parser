
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
    app = p.Application(FakeArgvParser(), None, None)
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
    app = p.Application(None, FakeWorkerFactory(), None)
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
    app = p.Application(None, None, None)
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
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), None)
    exitstatus = app.tryrun('argv')
    self.assertEqual(exitstatus, 'exitstatus')
    self.assertEqual(report, [
          ('parse', 'argv'),
          ('produce', 'options', 'argvunknown'),
          ('work', )])

class TestRun(unittest.TestCase):

  def test_noerror(self):
    class FakeArgvParser(object):
      def parse(self, argv):
        return 'options', 'argvunknown'
    class FakeWorkerFactory(object):
      def produce(self, options, argvunknown):
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        return 'exitstatus'
    stderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), stderr)
    exitstatus = app.run('argv')
    self.assertEqual(stderr.getvalue(), '')
    self.assertEqual(exitstatus, 'exitstatus')

  def test_genericerror(self):
    class FakeArgvParser(object):
      def parse(self, argv):
        return 'options', 'argvunknown'
    class FakeWorkerFactory(object):
      def produce(self, options, argvunknown):
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        raise p.Error('generic error')
    stderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), stderr)
    exitstatus = app.run('argv')
    self.assertEqual(stderr.getvalue(), 'generic error\n')
    self.assertEqual(exitstatus, 1)
