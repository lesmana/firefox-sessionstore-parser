
import unittest

import StringIO

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_error(self):
    report = []
    class FakeMain(object):
      def trymain(self, argv):
        report.append(('trymain', argv))
        raise p.MainError('silly error')
    fakemain = FakeMain()
    argv = ['wat']
    exitstatus, errormessage = p.Main.main.__func__(fakemain, argv)
    self.assertEqual(errormessage, 'silly error')
    self.assertEqual(exitstatus, 1)
    self.assertEqual(report, [
          ('trymain', ['wat'])])
