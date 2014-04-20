
import unittest

import sessionstoreparser as p

class TestGetWindowGeneratorClass(unittest.TestCase):

  def test_default(self):
    windowgeneratorfactory = p.UrlGeneratorFactory({
          'windowgenerator': 'windowgeneratorclass'})
    windowgeneratorclass = windowgeneratorfactory.getwindowgeneratorclass()
    self.assertEqual(windowgeneratorclass, 'windowgeneratorclass')

class TestGetTabGeneratorClass(unittest.TestCase):

  def test_default(self):
    tabgeneratorfactory = p.UrlGeneratorFactory({
          'tabgenerator': 'tabgeneratorclass'})
    tabgeneratorclass = tabgeneratorfactory.gettabgeneratorclass()
    self.assertEqual(tabgeneratorclass, 'tabgeneratorclass')

class TestGetUrlGeneratorClass(unittest.TestCase):

  def test_default(self):
    urlgeneratorfactory = p.UrlGeneratorFactory({
          'urlgenerator': 'urlgeneratorclass'})
    urlgeneratorclass = urlgeneratorfactory.geturlgeneratorclass()
    self.assertEqual(urlgeneratorclass, 'urlgeneratorclass')

class TestGetWindowGenerator(unittest.TestCase):

  def test_default(self):
    report = []
    class FakeWindowGenerator(object):
      def __new__(cls):
        report.append(('__init__', ))
        return 'fakewindowgenerator'
    class FakeUrlGeneratorFactory(object):
      def getwindowgeneratorclass(self):
        report.append(('getwindowgeneratorclass', ))
        return FakeWindowGenerator
    windowgenerator = p.UrlGeneratorFactory.getwindowgenerator.__func__(
          FakeUrlGeneratorFactory())
    self.assertEqual(windowgenerator, 'fakewindowgenerator')
    self.assertEqual(report, [
          ('getwindowgeneratorclass', ),
          ('__init__', )])

class TestGetTabGenerator(unittest.TestCase):

  def test_default(self):
    report = []
    class FakeTabGenerator(object):
      def __new__(cls, windowgenerator):
        report.append(('__init__', windowgenerator))
        return 'faketabgenerator'
    class FakeUrlGeneratorFactory(object):
      def gettabgeneratorclass(self):
        report.append(('gettabgeneratorclass', ))
        return FakeTabGenerator
    tabgenerator = p.UrlGeneratorFactory.gettabgenerator.__func__(
          FakeUrlGeneratorFactory(), 'windowgenerator')
    self.assertEqual(tabgenerator, 'faketabgenerator')
    self.assertEqual(report, [
          ('gettabgeneratorclass', ),
          ('__init__', 'windowgenerator')])

class TestGetUrlGenerator(unittest.TestCase):

  def test_default(self):
    report = []
    class FakeUrlGenerator(object):
      def __new__(cls, tabgenerator):
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

