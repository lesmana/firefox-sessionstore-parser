
import unittest

import sessionstoreparser as p

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

