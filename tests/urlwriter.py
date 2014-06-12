
import unittest

import StringIO

import sessionstoreparser as p

class TestWrite(unittest.TestCase):

  def test_empty(self):
    stringio = StringIO.StringIO()
    urlwriter = p.UrlWriter(stringio)
    urlwriter.write([])
    self.assertEqual(stringio.getvalue(), '')

  def test_someurls(self):
    stringio = StringIO.StringIO()
    urlwriter = p.UrlWriter(stringio)
    url1 = {'url': 'url1'}
    url2 = {'url': 'url2'}
    urlwriter.write([url1, url2])
    self.assertEqual(stringio.getvalue(), 'url1\nurl2\n')
