
import unittest

import StringIO

import sessionstoreparser as p

class TestRun(unittest.TestCase):

  def test_noerror(self):
    #pylint: disable=unused-argument
    class FakeArgvParser(object):
      def parse(self, argv):
        return {'options': 'options'}, ['argvunknown']
    class FakeWorkerFactory(object):
      def produce(self, options, argvunknown):
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        return 42
    stderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), stderr)
    exitstatus = app.run(['progname', 'argv'])
    self.assertEqual(stderr.getvalue(), '')
    self.assertEqual(exitstatus, 42)

  def test_genericerror(self):
    #pylint: disable=unused-argument
    class FakeArgvParser(object):
      def parse(self, argv):
        return {'options': 'options'}, ['argvunknown']
    class FakeWorkerFactory(object):
      def produce(self, options, argvunknown):
        return FakeWorker()
    class FakeWorker(object):
      def __call__(self):
        raise p.Error('generic error')
    stderr = StringIO.StringIO()
    app = p.Application(FakeArgvParser(), FakeWorkerFactory(), stderr)
    exitstatus = app.run(['progname', 'argv'])
    self.assertEqual(stderr.getvalue(), 'generic error\n')
    self.assertEqual(exitstatus, 1)
