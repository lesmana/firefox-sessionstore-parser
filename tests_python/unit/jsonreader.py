
import contextlib

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
      raise IOError('ignored error message')
    jsonreader = p.JsonReader(openfunc, None)
    try:
      _ = jsonreader.openfile('filename')
    except p.JsonReaderError as err:
      self.assertEqual(str(err), 'error: cannot open file filename.')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('openfunc', 'filename')])

class TestJsonLoad(unittest.TestCase):

  def test_default(self):
    report = []
    def jsonloadfunc(fileob):
      report.append(('jsonloadfunc', fileob))
      return 'sessionstore'
    jsonreader = p.JsonReader(None, jsonloadfunc)
    sessionstore = jsonreader.jsonload('fileob', 'filename')
    self.assertEqual(sessionstore, 'sessionstore')
    self.assertEqual(report, [
          ('jsonloadfunc', 'fileob')])

  def test_error(self):
    report = []
    def jsonloadfunc(fileob):
      report.append(('jsonloadfunc', fileob))
      raise ValueError('ignored error message')
    jsonreader = p.JsonReader(None, jsonloadfunc)
    try:
      _ = jsonreader.jsonload('fileob', 'filename')
    except p.JsonReaderError as err:
      self.assertEqual(str(err),
            'error: cannot read session store from file filename.')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('jsonloadfunc', 'fileob')])

class TestRead(unittest.TestCase):

  def test_default(self):
    report = []
    @contextlib.contextmanager
    def openfilecontext():
      report.append(('enter', ))
      yield 'fileob'
      report.append(('exit', ))
    class FakeJsonReader(object):
      def openfile(self, filename):
        report.append(('openfile', filename))
        return openfilecontext()
      def jsonload(self, fileob, filename):
        report.append(('jsonload', fileob, filename))
        return 'sessionstore'
    sessionstore = p.JsonReader.read.__func__(FakeJsonReader(), 'filename')
    self.assertEqual(sessionstore, 'sessionstore')
    self.assertEqual(report, [
          ('openfile', 'filename'),
          ('enter', ),
          ('jsonload', 'fileob', 'filename'),
          ('exit', )])

  def test_openfileerror(self):
    report = []
    class FakeJsonReader(object):
      def openfile(self, filename):
        report.append(('openfile', filename))
        raise p.JsonReaderError('silly error')
    try:
      _ = p.JsonReader.read.__func__(FakeJsonReader(), 'filename')
    except p.JsonReaderError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('openfile', 'filename')])

  def test_jsonloaderror(self):
    report = []
    @contextlib.contextmanager
    def openfilecontext():
      report.append(('enter', ))
      yield 'fileob'
    class FakeJsonReader(object):
      def openfile(self, filename):
        report.append(('openfile', filename))
        return openfilecontext()
      def jsonload(self, fileob, filename):
        report.append(('jsonload', fileob, filename))
        raise p.JsonReaderError('silly error')
    try:
      _ = p.JsonReader.read.__func__(FakeJsonReader(), 'filename')
    except p.JsonReaderError as err:
      self.assertEqual(str(err), 'silly error')
    else:
      self.fail('expected exception') # pragma: no cover
    self.assertEqual(report, [
          ('openfile', 'filename'),
          ('enter', ),
          ('jsonload', 'fileob', 'filename')])
