
import unittest

import sessionstoreparser as p

class TestGetUrlGenerator(unittest.TestCase):

  def test_default(self):
    report = []
    class FakeUrlGenerator(object):
      def __new__(self, tabgenerator):
        report.append(('__init__', tabgenerator))
        return 'fakeurlgenerator'
    class FakeUrlGeneratorFactory(object):
      def geturlgeneratorclass(self):
        report.append(('geturlgeneratorclass', ))
        return FakeUrlGenerator
    urlgenerator = p.UrlGeneratorFactory.geturlgenerator.__func__(
          FakeUrlGeneratorFactory(), 'tabgenerator')
    self.assertEqual(urlgenerator, 'fakeurlgenerator')
    self.assertEqual(report, [
          ('geturlgeneratorclass', ),
          ('__init__', 'tabgenerator')])

class TestProduce(unittest.TestCase):

  def test_default(self):
    report = []
    class FakeUrlGeneratorFactory(object):
      def getwindowgenerator(self):
        report.append(('getwindowgenerator', ))
        return 'windowgenerator'
      def gettabgenerator(self, windowgenerator):
        report.append(('gettabgenerator', windowgenerator))
        return 'tabgenerator'
      def geturlgenerator(self, tabgenerator):
        report.append(('geturlgenerator', tabgenerator))
        return 'urlgenerator'
    urlgenerator = p.UrlGeneratorFactory.produce.__func__(
          FakeUrlGeneratorFactory())
    self.assertEqual(urlgenerator, 'urlgenerator')
    self.assertEqual(report, [
          ('getwindowgenerator', ),
          ('gettabgenerator', 'windowgenerator'),
          ('geturlgenerator', 'tabgenerator')])

