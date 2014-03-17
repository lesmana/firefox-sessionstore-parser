
import unittest

import sessionstoreparser as p

class TestOpenFile(unittest.TestCase):

  def test_default(self):
    report = []
    def openfunc(filename):
      report.append(('openfunc', filename))
      return 'fileob'
    jsonreader = p.JsonReader(openfunc, None)
    fileob = jsonreader.openfile('filename')
    self.assertEqual(fileob, 'fileob')
    self.assertEqual(report, [
          ('openfunc', 'filename')])

  def test_error(self):
    report = []
    def openfunc(filename):
      report.append(('openfunc', filename))
      raise IOError('silly error')
    jsonreader = p.JsonReader(openfunc, None)
    try:
      _ = jsonreader.openfile('filename')
    except p.JsonReaderError as jre:
      self.assertEqual(str(jre), 'silly error')
    else:
      self.fail('expected exception')
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

  def test_error(self):
    report = []
    def jsonload(fileob):
      report.append(('jsonload', fileob))
      raise ValueError('silly error')
    jsonreader = p.JsonReader(None, jsonload)
    try:
      _ = jsonreader.jsonload('fileob')
    except p.JsonReaderError as jre:
      self.assertEqual(str(jre), 'silly error')
    else:
      self.fail('expected exception')
    self.assertEqual(report, [
          ('jsonload', 'fileob')])

class TestRead(unittest.TestCase):

  def test_default(self):
    report = []
    class OpenFileContext(object):
      def __enter__(self):
        report.append(('enter', ))
        return 'fileob'
      def __exit__(self, exc_type, exc_value, traceback):
        report.append(('exit', exc_type, exc_value, traceback))
    class FakeJsonReader(object):
      def openfile(self, filename):
        report.append(('openfile', filename))
        return OpenFileContext()
      def jsonload(self, fileob):
        report.append(('jsonload', fileob))
        return 'sessionstore'
    sessionstore = p.JsonReader.read.__func__(FakeJsonReader(), 'filename')
    self.assertEqual(sessionstore, 'sessionstore')
    self.assertEqual(report, [
          ('openfile', 'filename'),
          ('enter', ),
          ('jsonload', 'fileob'),
          ('exit', None, None, None)])
