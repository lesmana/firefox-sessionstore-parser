
# this file is named sessionstoreparsertest to avoid name conflict

import unittest

import sessionstoreparser as p

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
        return ['filtered', 'urls']
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
          ('write', ['filtered', 'urls'])])
