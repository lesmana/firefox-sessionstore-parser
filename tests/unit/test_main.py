
import unittest

import StringIO

import sessionstoreparser as p

class TestMain(unittest.TestCase):

  def test_nofilename(self):
    mainobject = p.Main(None, None)
    argv = ['wat']
    exitstatus, errormessage = mainobject.main(argv)
    self.assertEqual(errormessage, 'need filename')
    self.assertEqual(exitstatus, 1)
