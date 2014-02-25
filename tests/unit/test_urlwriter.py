
import unittest

import StringIO

import sessionstoreparser as p

class TestWrite(unittest.TestCase):

  def test_empty(self):
    report = []
    stringio = StringIO.StringIO()
    urlwriter = p.UrlWriter(stringio)
    urlwriter.write([])
    self.assertEqual(stringio.getvalue(), '')

  def test_someurls(self):
    report = []
    stringio = StringIO.StringIO()
    urlwriter = p.UrlWriter(stringio)
    urlwriter.write(['url1', 'url2'])
    self.assertEqual(stringio.getvalue(), 'url1\nurl2\n')
