
import unittest

import StringIO

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_nofilename(self):
    report = []
    class FakeMain(object):
      def trymain(self, argv):
        report.append(('trymain', argv))
        raise p.MainError('need filename')
    fakemain = FakeMain()
    argv = ['wat']
    exitstatus, errormessage = p.Main.main.__func__(fakemain, argv)
    self.assertEqual(errormessage, 'need filename')
    self.assertEqual(exitstatus, 1)
