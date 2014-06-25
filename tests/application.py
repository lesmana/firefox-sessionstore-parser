
import unittest

import StringIO

import sessionstoreparser as p

class TestRun(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvParser(object):
      def parse(self, argv):
        report.append(('parse', argv))
        return {'parsedargv': 'parsedargv'}
    class FakeWorkerFactory(object):
      def produce(self, parsedargv):
        report.append(('produce', parsedargv))
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        report.append(('work', ))
        return 42
    stderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), stderr)
    exitstatus = app.run(['progname', 'argv'])
    self.assertEqual(stderr.getvalue(), '')
    self.assertEqual(exitstatus, 42)
    self.assertEqual(report, [
          ('parse', ['progname', 'argv']),
          ('produce', {'parsedargv': 'parsedargv'}),
          ('work', )])

  def test_genericerror(self):
    report = []
    class FakeArgvParser(object):
      def parse(self, argv):
        report.append(('parse', argv))
        return {'parsedargv': 'parsedargv'}
    class FakeWorkerFactory(object):
      def produce(self, parsedargv):
        report.append(('produce', parsedargv))
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        report.append(('work', ))
        raise p.Error('generic error')
    stderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), stderr)
    exitstatus = app.run(['progname', 'argv'])
    self.assertEqual(stderr.getvalue(), 'generic error\n')
    self.assertEqual(exitstatus, 1)
    self.assertEqual(report, [
          ('parse', ['progname', 'argv']),
          ('produce', {'parsedargv': 'parsedargv'}),
          ('work', )])
