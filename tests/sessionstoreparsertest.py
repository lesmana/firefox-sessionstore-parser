
# this file is named sessionstoreparsertest to avoid name conflict

import unittest

import sessionstoreparser as p

class TestGetSessionStore(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeJsonReader(object):
      def read(self, filename):
        report.append(('read', filename))
        return {'json': 'object'}
    parser = p.SessionStoreParser(FakeJsonReader(), None, None, None)
    sessionstore = parser.getsessionstore('filename')
    self.assertEqual(sessionstore, {'json': 'object'})
    self.assertEqual(report, [
          ('read', 'filename')])

class TestGetUrls(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeUrlGenerator(object):
      def generate(self, sessionstore):
        report.append(('generate', sessionstore))
        return ['urls']
    parser = p.SessionStoreParser(None, FakeUrlGenerator(), None, None)
    urls = parser.geturls({'session': 'store'})
    self.assertEqual(urls, ['urls'])
    self.assertEqual(report, [
          ('generate', {'session': 'store'})])

class TestWriteUrls(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeUrlWriter(object):
      def write(self, urls):
        report.append(('write', urls))
    parser = p.SessionStoreParser(None, None, None, FakeUrlWriter())
    parser.writeurls(['urls'])
    self.assertEqual(report, [
          ('write', ['urls'])])

class TestSessionStoreParse(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeJsonReader(object):
      def read(self, filename):
        report.append(('read', filename))
        return {'json': 'object'}
    class FakeUrlGenerator(object):
      def generate(self, sessionstore):
        report.append(('generate', sessionstore))
        return ['urls']
    class FakeUrlFilter(object):
      def filter(self, urls):
        report.append(('filter', urls))
        return urls
    class FakeUrlWriter(object):
      def write(self, urls):
        report.append(('write', urls))
    parser = p.SessionStoreParser(
          FakeJsonReader(), FakeUrlGenerator(), FakeUrlFilter(), FakeUrlWriter())
    parser.parse('filename')
    self.assertEqual(report, [
          ('read', 'filename'),
          ('generate', {'json': 'object'}),
          ('filter', ['urls']),
          ('write', ['urls'])])
