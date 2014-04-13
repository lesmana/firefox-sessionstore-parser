
import unittest

import sessionstoreparser as p

class TestHandle(unittest.TestCase):

  def test_filename(self):
    argvhandler = p.ArgvHandler()
    options = argvhandler.handle(['progname', 'filename'])
    self.assertEqual(options, {'filename': 'filename'})

  def test_nofilename(self):
    argvhandler = p.ArgvHandler()
    try:
      _ = argvhandler.handle(['progname'])
    except p.ArgvError as err:
      self.assertEqual(str(err), 'need filename')
    else:
      self.fail('expected exception') # pragma: no cover
