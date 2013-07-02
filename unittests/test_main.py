
import unittest

import StringIO

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_nofilename(self):
    stdout = StringIO.StringIO()
    mainobject = p.Main(stdout, None)
    argv = ['wat']
    exitstatus = mainobject.main(argv)
    self.assertEqual(stdout.getvalue(), 'need filename')
    self.assertEqual(exitstatus, 1)

  def test_filename(self):
    report = []
    class PartFakeMain(p.Main):
      def getsessionstore(self, filename):
        report.append(('getsessionstore', filename))
        return 'sessionstore'
      def printopenurls(self, sessionstore):
        report.append(('printopenurls', sessionstore))
    stdout = StringIO.StringIO()
    mainobject = PartFakeMain(stdout, None)
    argv = ['wat', 'filename']
    exitstatus = mainobject.main(argv)
    self.assertEqual(stdout.getvalue(), '')
    self.assertEqual(exitstatus, 0)
    self.assertEqual(report, [
          ('getsessionstore', 'filename'),
          ('printopenurls', 'sessionstore')])
