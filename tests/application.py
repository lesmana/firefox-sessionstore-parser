
import unittest

import StringIO

import sessionstoreparser as p

class TestRun(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvParser(object):
      def parse(self, argv):
        report.append(('parse', argv))
        return {'parsed': 'argv'}, ['rest']
    class FakeWorkerFactory(object):
      def make(self, parsedargv, rest):
        report.append(('make', parsedargv, rest))
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        report.append(('work', ))
        return 42
    fakestderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), fakestderr)
    exitstatus = app.run(['progname', 'argv'])
    self.assertEqual(fakestderr.getvalue(), '')
    self.assertEqual(exitstatus, 42)
    self.assertEqual(report, [
          ('parse', ['progname', 'argv']),
          ('make', {'parsed': 'argv'}, ['rest']),
          ('work', )])

  def test_genericerror(self):
    report = []
    class FakeArgvParser(object):
      def parse(self, argv):
        report.append(('parse', argv))
        return {'parsed': 'argv'}, ['rest']
    class FakeWorkerFactory(object):
      def make(self, parsedargv, rest):
        report.append(('make', parsedargv, rest))
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        report.append(('work', ))
        raise p.Error('generic error')
    fakestderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), fakestderr)
    exitstatus = app.run(['progname', 'argv'])
    self.assertEqual(fakestderr.getvalue(), 'generic error\n')
    self.assertEqual(exitstatus, 1)
    self.assertEqual(report, [
          ('parse', ['progname', 'argv']),
          ('make', {'parsed': 'argv'}, ['rest']),
          ('work', )])
