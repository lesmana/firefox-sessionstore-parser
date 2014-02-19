
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

  def test_filename(self):
    report = []
    def fakegetsessionstore(filename):
      report.append(('getsessionstore', filename))
      return 'sessionstore'
    def fakegetparser():
      report.append(('getparser', ))
      return 'parser'
    def fakeprinturls(parser, sessionstore):
      report.append(('printurls', parser, sessionstore))
    mainobject = p.Main(None, None)
    mainobject.getsessionstore = fakegetsessionstore
    mainobject.getparser = fakegetparser
    mainobject.printurls = fakeprinturls
    argv = ['wat', 'filename']
    exitstatus, errormessage = mainobject.main(argv)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(errormessage, None)
    self.assertEqual(report, [
          ('getsessionstore', 'filename'),
          ('getparser', ),
          ('printurls', 'parser', 'sessionstore')])
