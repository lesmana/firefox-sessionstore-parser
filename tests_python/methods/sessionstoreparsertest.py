
# this file is named sessionstoreparsertest to avoid name conflict

import unittest

import StringIO

import sessionstoreparser as p

class TestGetSessionStore(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeJsonReader(object):
      def read(self, filename):
        report.append(('read', filename))
        return 'jsonobject'
    parser = p.SessionStoreParser(FakeJsonReader(), None, None)
    sessionstore = parser.getsessionstore({'filename': 'filename'})
    self.assertEqual(sessionstore, 'jsonobject')
    self.assertEqual(report, [
          ('read', 'filename')])

class TestGetUrlGenerator(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeUrlGeneratorFactory(object):
      def produce(self):
        report.append(('produce', ))
        return 'urlgenerator'
    parser = p.SessionStoreParser(None, FakeUrlGeneratorFactory(), None)
    urlgenerator = parser.geturlgenerator()
    self.assertEqual(urlgenerator, 'urlgenerator')
    self.assertEqual(report, [
          ('produce', )])

class TestGetUrls(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeUrlGenerator(object):
      def generate(self, sessionstore):
        report.append(('generate', sessionstore))
        return 'urls'
    parser = p.SessionStoreParser(None, None, None)
    urls = parser.geturls(FakeUrlGenerator(), 'sessionstore')
    self.assertEqual(urls, 'urls')
    self.assertEqual(report, [
          ('generate', 'sessionstore')])

class TestWriteUrls(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeUrlWriter(object):
      def write(self, urls):
        report.append(('write', urls))
    app = p.Application(None, None, None, FakeUrlWriter())
    app.writeurls('urls')
    self.assertEqual(report, [
          ('write', 'urls')])
