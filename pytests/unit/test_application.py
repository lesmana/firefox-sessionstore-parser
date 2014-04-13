
import unittest

import sessionstoreparser as p

class TestHandleArgv(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeArgvHandler(object):
      def handle(self, argv):
        report.append(('handle', argv))
        return 'filename'
    app = p.Application(FakeArgvHandler(), None, None, None)
    options = app.handleargv('argv')
    self.assertEqual(options, {'filename': 'filename'})
    self.assertEqual(report, [
          ('handle', 'argv')])

class TestGetSessionStore(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeJsonReader(object):
      def read(self, filename):
        report.append(('read', filename))
        return 'jsonobject'
    app = p.Application(None, FakeJsonReader(), None, None)
    sessionstore = app.getsessionstore({'filename': 'filename'})
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
    app = p.Application(None, None, FakeUrlGeneratorFactory(), None)
    urlgenerator = app.geturlgenerator()
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
    app = p.Application(None, None, None, None)
    urls = app.geturls(FakeUrlGenerator(), 'sessionstore')
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

class TestTryRun(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeApplication(object):
      def handleargv(self, argv):
        report.append(('handleargv', argv))
        return 'options'
      def getsessionstore(self, options):
        report.append(('getsessionstore', options))
        return 'sessionstore'
      def geturlgenerator(self):
        report.append(('geturlgenerator', ))
        return 'urlgenerator'
      def geturls(self, urlgenerator, sessionstore):
        report.append(('geturls', urlgenerator, sessionstore))
        return 'urls'
      def writeurls(self, urls):
        report.append(('writeurls', urls))
    fakeapp = FakeApplication()
    p.Application.tryrun.__func__(fakeapp, 'argv')
    self.assertEqual(report, [
          ('handleargv', 'argv'),
          ('getsessionstore', 'options'),
          ('geturlgenerator', ),
          ('geturls', 'urlgenerator', 'sessionstore'),
          ('writeurls', 'urls')])

class TestRun(unittest.TestCase):

  def test_noerror(self):
    report = []
    class FakeApplication(object):
      def tryrun(self, argv):
        report.append(('tryrun', argv))
    fakeapp = FakeApplication()
    exitstatus, errormessage = p.Application.run.__func__(fakeapp, 'argv')
    self.assertEqual(errormessage, None)
    self.assertEqual(exitstatus, 0)
    self.assertEqual(report, [
          ('tryrun', 'argv')])

  def test_argverror(self):
    report = []
    class FakeApplication(object):
      def tryrun(self, argv):
        report.append(('tryrun', argv))
        raise p.ArgvError('argv error')
    fakeapp = FakeApplication()
    exitstatus, errormessage = p.Application.run.__func__(fakeapp, 'argv')
    self.assertEqual(errormessage, 'argv error')
    self.assertEqual(exitstatus, 2)
    self.assertEqual(report, [
          ('tryrun', 'argv')])

  def test_genericerror(self):
    report = []
    class FakeApplication(object):
      def tryrun(self, argv):
        report.append(('tryrun', argv))
        raise p.Error('generic error')
    fakeapp = FakeApplication()
    exitstatus, errormessage = p.Application.run.__func__(fakeapp, 'argv')
    self.assertEqual(errormessage, 'generic error')
    self.assertEqual(exitstatus, 1)
    self.assertEqual(report, [
          ('tryrun', 'argv')])
