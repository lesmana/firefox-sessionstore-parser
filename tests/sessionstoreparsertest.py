
# this file is named sessionstoreparsertest to avoid name conflict

import unittest

import sessionstoreparser as p

class TestGetSessionStore(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeJsonReader(object):
      def read(self, filename):
        report.append(('read', filename))
        return 'jsonobject'
    parser = p.SessionStoreParser(FakeJsonReader(), None, None)
    sessionstore = parser.getsessionstore('filename')
    self.assertEqual(sessionstore, 'jsonobject')
    self.assertEqual(report, [
          ('read', 'filename')])

class TestGetUrls(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeUrlGenerator(object):
      def generate(self, sessionstore):
        report.append(('generate', sessionstore))
        return 'urls'
    parser = p.SessionStoreParser(None, FakeUrlGenerator(), None)
    urls = parser.geturls('sessionstore')
    self.assertEqual(urls, 'urls')
    self.assertEqual(report, [
          ('generate', 'sessionstore')])

class TestWriteUrls(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeUrlWriter(object):
      def write(self, urls):
        report.append(('write', urls))
    parser = p.SessionStoreParser(None, None, FakeUrlWriter())
    parser.writeurls('urls')
    self.assertEqual(report, [
          ('write', 'urls')])
