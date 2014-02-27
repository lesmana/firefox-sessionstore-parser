
import unittest

import sessionstoreparser as p

class TestGetContextManageable(unittest.TestCase):

  def test_default(self):
    report = []
    def openfunc(filename):
      report.append(('openfunc', filename))
      return 'fileob'
    jsonreader = p.JsonReader(openfunc, None)
    fileob = jsonreader.getcontextmanageable('filename')
    self.assertEqual(fileob, 'fileob')
    self.assertEqual(report, [
          ('openfunc', 'filename')])

class TestJsonLoad(unittest.TestCase):

  def test_default(self):
    report = []
    def jsonload(fileob):
      report.append(('jsonload', fileob))
      return 'sessionstore'
    jsonreader = p.JsonReader(None, jsonload)
    sessionstore = jsonreader.jsonload('fileob')
    self.assertEqual(sessionstore, 'sessionstore')
    self.assertEqual(report, [
          ('jsonload', 'fileob')])

class TestRead(unittest.TestCase):

  def test_default(self):
    report = []
    class ContextManageable(object):
      def __enter__(self):
        report.append(('enter', ))
        return 'fileob'
      def __exit__(self, exc_type, exc_value, traceback):
        report.append(('exit', exc_type, exc_value, traceback))
    class FakeJsonReader(object):
      def getcontextmanageable(self, filename):
        report.append(('getcontextmanageable', filename))
        return ContextManageable()
      def jsonload(self, fileob):
        report.append(('jsonload', fileob))
        return 'sessionstore'
    sessionstore = p.JsonReader.read.__func__(FakeJsonReader(), 'filename')
    self.assertEqual(sessionstore, 'sessionstore')
    self.assertEqual(report, [
          ('getcontextmanageable', 'filename'),
          ('enter', ),
          ('jsonload', 'fileob'),
          ('exit', None, None, None)])
