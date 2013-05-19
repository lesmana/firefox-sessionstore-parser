
# copy from unittestchooser git repository checkout 266ac45

import StringIO
import getopt
import inspect
import itertools
import operator
import sys
import unittest

# =============================================================================
class Error(Exception):

  # ---------------------------------------------------------------------------
  def __init__(self, message):
    # ignore not calling super: pylint: disable=W0231
    self.message = message

  # ---------------------------------------------------------------------------
  def __str__(self):
    return str(self.message)

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return '%s(%r)' % (self.__class__.__name__,
          self.message)

# =============================================================================
class QueryError(Error):

  # ---------------------------------------------------------------------------
  def __init__(self, message, element):
    super(QueryError, self).__init__(message)
    self.element = element

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return '%s(%r, %r)' % (self.__class__.__name__,
          self.message, self.element)

# =============================================================================
class FilterError(Error):

  # ---------------------------------------------------------------------------
  def __init__(self, message, pattern, element):
    super(FilterError, self).__init__(message)
    self.pattern = pattern
    self.element = element

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return '%s(%r, %r, %r)' % (self.__class__.__name__,
          self.message, self.pattern, self.element)

# =============================================================================
class ArgvError(Error):

  # ---------------------------------------------------------------------------
  def __init__(self, message, option):
    super(ArgvError, self).__init__(message)
    self.option = option

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return '%s(%r, %r)' % (self.__class__.__name__,
          self.message, self.option)

# =============================================================================
class Path(object):

  # ---------------------------------------------------------------------------
  def __init__(self, elements):
    self.elements = elements

  # ---------------------------------------------------------------------------
  def __eq__(self, other):
    try:
      otherelements = other.elements
    except AttributeError:
      return False
    return self.elements == otherelements

  # ---------------------------------------------------------------------------
  def __hash__(self):
    return hash(self.elements)

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return '%s(%r)' % (self.__class__.__name__, self.elements)

  # ---------------------------------------------------------------------------
  @classmethod
  def fromiterable(cls, iterable):
    elements = tuple(iterable)
    instance = cls(elements)
    return instance

  # ---------------------------------------------------------------------------
  def toiterable(self):
    return list(self.elements)

  # ---------------------------------------------------------------------------
  def tostring(self):
    string = '.'.join(self.elements)
    return string

# =============================================================================
class Info(object):

  # ---------------------------------------------------------------------------
  def __init__(self, path, testclass, methodname):
    self.path = path
    self.testclass = testclass
    self.methodname = methodname

  # ---------------------------------------------------------------------------
  def __eq__(self, other):
    try:
      otherpath = other.path
      othertestclass = other.testclass
      othermethodname = other.methodname
    except AttributeError:
      return False
    return all([
          self.path == otherpath,
          self.testclass == othertestclass,
          self.methodname == othermethodname])

  # ---------------------------------------------------------------------------
  __hash__ = None

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return '%s(%r, %r, %r)' % (self.__class__.__name__,
          self.path, self.testclass, self.methodname)

  # ---------------------------------------------------------------------------
  @staticmethod
  def returnfullname(otherself):
    # ignore use of double underscore variable: pylint: disable=W0212
    return otherself.__fullname

  # ---------------------------------------------------------------------------
  def hackfullname(self, testinstance, testclass):
    # ignore use of double underscore variable: pylint: disable=W0212
    fullname = self.path.tostring()
    testinstance.__fullname = fullname
    testclass.__str__ = self.returnfullname

  # ---------------------------------------------------------------------------
  def createinstance(self):
    testinstance = self.testclass(self.methodname)
    self.hackfullname(testinstance, self.testclass)
    return testinstance

# =============================================================================
class Collection(object):

  # ---------------------------------------------------------------------------
  def __init__(self, infodict):
    self.infodict = infodict

  # ---------------------------------------------------------------------------
  def __eq__(self, other):
    try:
      otherinfodict = other.infodict
    except AttributeError:
      return False
    return self.infodict == otherinfodict

  # ---------------------------------------------------------------------------
  __hash__ = None

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return '%s(%r)' % (self.__class__.__name__, self.infodict)

  # ---------------------------------------------------------------------------
  @classmethod
  def frominfos(cls, infos):
    infodict = {}
    for info in infos:
      infodict[info.path] = info
    instance = cls(infodict)
    return instance

  # ---------------------------------------------------------------------------
  def newfrompaths(self, paths):
    newinfodict = {}
    for path in paths:
      newinfodict[path] = self.infodict[path]
    newcollection = self.__class__(newinfodict)
    return newcollection

  # ---------------------------------------------------------------------------
  def sortedpaths(self, paths):
    getelementsfunc = operator.attrgetter('elements')
    sortedpaths = sorted(paths, key = getelementsfunc)
    return sortedpaths

  # ---------------------------------------------------------------------------
  def getinfos(self):
    infos = []
    paths = self.infodict.keys()
    for path in self.sortedpaths(paths):
      info = self.infodict[path]
      infos.append(info)
    return infos

  # ---------------------------------------------------------------------------
  def getpaths(self):
    paths = self.infodict.keys()
    sortedpaths = self.sortedpaths(paths)
    return sortedpaths

# =============================================================================
class Collector(object):
  default = object()
  defaultmethodprefixes = ['test']
  defaultskipmodules = ['unittest']

  # ---------------------------------------------------------------------------
  def __init__(self,
        methodprefixes = default,
        skipmodules = default):
    if methodprefixes is self.default:
      methodprefixes = self.defaultmethodprefixes
    if skipmodules is self.default:
      skipmodules = self.defaultskipmodules
    self.methodprefixes = methodprefixes
    self.skipmodules = skipmodules

  # ---------------------------------------------------------------------------
  def namesfromtestcase(self, testcase):
    for name in dir(testcase):
      for prefix in self.methodprefixes:
        if name.startswith(prefix):
          attr = getattr(testcase, name)
          if callable(attr):
            yield name

  # ---------------------------------------------------------------------------
  def testcasesfrommodule(self, module):
    for name in dir(module):
      attr = getattr(module, name)
      if inspect.isclass(attr):
        if issubclass(attr, unittest.TestCase):
          yield name, attr

  # ---------------------------------------------------------------------------
  def modulesfrommodule(self, module):
    for name in dir(module):
      if name not in self.skipmodules:
        attr = getattr(module, name)
        if inspect.ismodule(attr):
          yield name, attr

  # ---------------------------------------------------------------------------
  def modulesfrommoduletree(self, modobj, modpath = None, visited = None):
    if visited is None:
      visited = set()
    visited.add(modobj)
    if modpath is None:
      modpath = ()
    yield modpath, modobj
    for submodname, submodobj in self.modulesfrommodule(modobj):
      if submodobj not in visited:
        submodpath = modpath + (submodname, )
        for recmodpath, recmodobj in self.modulesfrommoduletree(
              submodobj, submodpath, visited):
          yield recmodpath, recmodobj

  # ---------------------------------------------------------------------------
  def infosfrommoduletree(self, module):
    for modpath, modobj in self.modulesfrommoduletree(module):
      for testcasename, testcase in self.testcasesfrommodule(modobj):
        for testmethodname in self.namesfromtestcase(testcase):
          plainpath = modpath + (testcasename, testmethodname)
          path = Path.fromiterable(plainpath)
          info = Info(path, testcase, testmethodname)
          yield info

  # ---------------------------------------------------------------------------
  def collectionfrominfos(self, infos):
    collection = Collection.frominfos(infos)
    return collection

  # ---------------------------------------------------------------------------
  def collect(self, module):
    infos = self.infosfrommoduletree(module)
    collection = self.collectionfrominfos(infos)
    return collection

# =============================================================================
class QueryTree(object):

  # ---------------------------------------------------------------------------
  def __init__(self, tree, leafsentinel):
    self.tree = tree
    self.leafsentinel = leafsentinel

  # ---------------------------------------------------------------------------
  def subtreeatpath(self, pathelements):
    subtree = self.tree
    for pathelement in pathelements:
      if pathelement in subtree:
        subtree = subtree[pathelement]
      else:
        raise QueryError('unable to match element %r' % pathelement,
              pathelement)
    return subtree

  # ---------------------------------------------------------------------------
  def pathsfromtree(self, tree):
    allpaths = set()
    for name, subtree in tree.items():
      if name is self.leafsentinel:
        paths = subtree
      else:
        paths = self.pathsfromtree(subtree)
      allpaths.update(paths)
    return allpaths

  # ---------------------------------------------------------------------------
  def query(self, pathelements):
    matchingtree = self.subtreeatpath(pathelements)
    matchingpaths = self.pathsfromtree(matchingtree)
    return matchingpaths

# =============================================================================
class QueryTreeFactory(object):
  default = object()
  defaultquerytreeclass = QueryTree
  defaultleafsentinel = '-'

  # ---------------------------------------------------------------------------
  def __init__(self, querytreeclass = default, leafsentinel = default):
    if querytreeclass is self.default:
      querytreeclass = self.defaultquerytreeclass
    if leafsentinel is self.default:
      leafsentinel = self.defaultleafsentinel
    self.querytreeclass = querytreeclass
    self.leafsentinel = leafsentinel

  # ---------------------------------------------------------------------------
  def branchesfrompath(self, path):
    branches = []
    last = (self.leafsentinel, set([path]))
    for pathelement in reversed(path.toiterable()):
      branch = (pathelement, last)
      branches.append(branch)
      last = branch
    return branches

  # ---------------------------------------------------------------------------
  def branchesfrompaths(self, paths):
    allbranches = []
    for path in paths:
      branches = self.branchesfrompath(path)
      allbranches.extend(branches)
    return allbranches

  # ---------------------------------------------------------------------------
  def treefrombranches(self, branches):
    namefunc = operator.itemgetter(0)
    sortedbranches = sorted(branches, key = namefunc)
    groupbyname = itertools.groupby(sortedbranches, key = namefunc)
    tree = {}
    for name, group in groupbyname:
      subbranches = [member[1] for member in group]
      if name is self.leafsentinel:
        subtree = set.union(*subbranches)
      else:
        subtree = self.treefrombranches(subbranches)
      tree[name] = subtree
    return tree

  # ---------------------------------------------------------------------------
  def treefrompaths(self, paths):
    branches = self.branchesfrompaths(paths)
    tree = self.treefrombranches(branches)
    return tree

  # ---------------------------------------------------------------------------
  def build(self, paths):
    tree = self.treefrompaths(paths)
    querytree = self.querytreeclass(tree, self.leafsentinel)
    return querytree

# =============================================================================
class PathFilter(object):
  default = object()
  defaultquerytreefactoryclass = QueryTreeFactory

  # ---------------------------------------------------------------------------
  def __init__(self, querytreefactory = default):
    if querytreefactory is self.default:
      querytreefactory = self.defaultquerytreefactoryclass()
    self.querytreefactory = querytreefactory

  # ---------------------------------------------------------------------------
  def buildquerytree(self, paths):
    querytree = self.querytreefactory.build(paths)
    return querytree

  # ---------------------------------------------------------------------------
  def elementsfrompattern(self, pattern):
    path = tuple(pattern.split('.'))
    return path

  # ---------------------------------------------------------------------------
  def pathsmatchingpatternelements(self, querytree, patternelements):
    matchingpaths = querytree.query(patternelements)
    return matchingpaths

  # ---------------------------------------------------------------------------
  def pathsmatchingpattern(self, querytree, pattern):
    patternelements = self.elementsfrompattern(pattern)
    try:
      matchingpaths = self.pathsmatchingpatternelements(querytree,
            patternelements)
    except QueryError as error:
      element = error.element
      raise FilterError('unable to match element %r of pattern %r' % (
            element, pattern), pattern, element)
    return matchingpaths

  # ---------------------------------------------------------------------------
  def parsepatterns(self, patterns):
    for pattern in patterns:
      if pattern.startswith('^'):
        negated = True
        pattern = pattern[1:]
      else:
        negated = False
      yield negated, pattern

  # ---------------------------------------------------------------------------
  def updatematchingpaths(self, allmatchingpaths, matchingpaths, subtract):
    if subtract:
      allmatchingpaths.difference_update(matchingpaths)
    else:
      allmatchingpaths.update(matchingpaths)

  # ---------------------------------------------------------------------------
  def pathsmatchingpatterns(self, querytree, patterns):
    allmatchingpaths = set([])
    for negated, pattern in self.parsepatterns(patterns):
      matchingpaths = self.pathsmatchingpattern(querytree, pattern)
      self.updatematchingpaths(allmatchingpaths, matchingpaths, negated)
    return allmatchingpaths

  # ---------------------------------------------------------------------------
  def filter(self, paths, patterns):
    querytree = self.buildquerytree(paths)
    matchingpaths = self.pathsmatchingpatterns(querytree, patterns)
    return matchingpaths

# =============================================================================
class FilteredCollector(object):
  default = object()
  defaultcollectorclass = Collector
  defaultpathfilterclass = PathFilter

  # ---------------------------------------------------------------------------
  def __init__(self,
        collector = default,
        pathfilter = default,
        patterns = None):
    if collector is self.default:
      collector = self.defaultcollectorclass()
    if pathfilter is self.default:
      pathfilter = self.defaultpathfilterclass()
    self.collector = collector
    self.pathfilter = pathfilter
    self.patterns = patterns

  # ---------------------------------------------------------------------------
  def pathsfromcollection(self, collection):
    paths = collection.getpaths()
    return paths

  # ---------------------------------------------------------------------------
  def dofilter(self, paths, patterns):
    matchingpaths = self.pathfilter.filter(paths, patterns)
    return matchingpaths

  # ---------------------------------------------------------------------------
  def collectionmatchingpaths(self, collection, paths):
    matchingcollection = collection.newfrompaths(paths)
    return matchingcollection

  # ---------------------------------------------------------------------------
  def collect(self, module):
    collection = self.collector.collect(module)
    paths = self.pathsfromcollection(collection)
    matchingpaths = self.dofilter(paths, self.patterns)
    matchingcollection = self.collectionmatchingpaths(
          collection, matchingpaths)
    return matchingcollection

# =============================================================================
class CollectorFactory(object):
  default = object()
  defaultcollectorclass = Collector
  defaultfilteredcollectorclass = FilteredCollector

  # ---------------------------------------------------------------------------
  def __init__(self,
        collectorclass = default,
        filteredcollectorclass = default):
    if collectorclass is self.default:
      collectorclass = self.defaultcollectorclass
    if filteredcollectorclass is self.default:
      filteredcollectorclass = self.defaultfilteredcollectorclass
    self.collectorclass = collectorclass
    self.filteredcollectorclass = filteredcollectorclass

  # ---------------------------------------------------------------------------
  def buildplaincollector(self):
    plaincollector = self.collectorclass()
    return plaincollector

  # ---------------------------------------------------------------------------
  def buildfilteredcollector(self, patterns):
    plaincollector = self.buildplaincollector()
    filteredcollector = self.filteredcollectorclass(
          collector = plaincollector,
          patterns = patterns)
    return filteredcollector

  # ---------------------------------------------------------------------------
  def build(self, patterns = None):
    if patterns is None:
      collector = self.buildplaincollector()
    else:
      collector = self.buildfilteredcollector(patterns)
    return collector

# =============================================================================
class NamePrinter(object):

  # ---------------------------------------------------------------------------
  def __init__(self):
    pass

  # ---------------------------------------------------------------------------
  def namefrompath(self, path):
    name = path.tostring()
    return name

  # ---------------------------------------------------------------------------
  def namelistfrompaths(self, paths):
    namelist = []
    for path in paths:
      name = self.namefrompath(path)
      namelist.append(name)
    return namelist

  # ---------------------------------------------------------------------------
  def stringfromnamelist(self, namelist):
    output = ''
    for name in sorted(namelist):
      output += name + '\n'
    return output

  # ---------------------------------------------------------------------------
  def print_(self, collection):
    paths = collection.getpaths()
    namelist = self.namelistfrompaths(paths)
    output = self.stringfromnamelist(namelist)
    return output

# =============================================================================
class SuiteFactory(object):
  default = object()
  defaultsuiteclass = unittest.TestSuite

  # ---------------------------------------------------------------------------
  def __init__(self,
        suiteclass = default):
    if suiteclass is self.default:
      suiteclass = self.defaultsuiteclass
    self.suiteclass = suiteclass

  # ---------------------------------------------------------------------------
  def infosfromcollection(self, collection):
    infos = collection.getinfos()
    return infos

  # ---------------------------------------------------------------------------
  def instancefrominfo(self, info):
    instance = info.createinstance()
    return instance

  # ---------------------------------------------------------------------------
  def instancesfrominfos(self, infos):
    instances = []
    for info in infos:
      instance = self.instancefrominfo(info)
      instances.append(instance)
    return instances

  # ---------------------------------------------------------------------------
  def suitefrominstances(self, instances):
    suite = self.suiteclass(instances)
    return suite

  # ---------------------------------------------------------------------------
  def build(self, collection):
    infos = self.infosfromcollection(collection)
    instances = self.instancesfrominfos(infos)
    suite = self.suitefrominstances(instances)
    return suite

# =============================================================================
class Runner(object):
  default = object()
  defaulttestrunnerclass = unittest.TextTestRunner

  # ---------------------------------------------------------------------------
  def __init__(self,
        testrunnerclass = default):
    if testrunnerclass is self.default:
      testrunnerclass = self.defaulttestrunnerclass
    self.testrunnerclass = testrunnerclass

  # ---------------------------------------------------------------------------
  def run(self, suite, verbosity):
    stream = StringIO.StringIO()
    testrunner = self.testrunnerclass(stream = stream, verbosity = verbosity)
    testresult = testrunner.run(suite)
    output = stream.getvalue()
    result = testresult.wasSuccessful()
    return output, result

# =============================================================================
class Worker(object):
  default = object()
  defaultcollectorfactoryclass = CollectorFactory
  defaultnameprinterclass = NamePrinter
  defaultsuitefactoryclass = SuiteFactory
  defaultrunnerclass = Runner

  # ---------------------------------------------------------------------------
  def __init__(self,
        collectorfactory = default,
        nameprinterclass = default,
        suitefactoryclass = default,
        runnerclass = default):
    if collectorfactory is self.default:
      collectorfactory = self.defaultcollectorfactoryclass()
    if nameprinterclass is self.default:
      nameprinterclass = self.defaultnameprinterclass
    if suitefactoryclass is self.default:
      suitefactoryclass = self.defaultsuitefactoryclass
    if runnerclass is self.default:
      runnerclass = self.defaultrunnerclass
    self.collectorfactory = collectorfactory
    self.nameprinterclass = nameprinterclass
    self.suitefactoryclass = suitefactoryclass
    self.runnerclass = runnerclass

  # ---------------------------------------------------------------------------
  def collectinfos(self, module, patterns = None):
    collector = self.collectorfactory.build(patterns = patterns)
    collection = collector.collect(module = module)
    return collection

  # ---------------------------------------------------------------------------
  def printname(self, module, patterns):
    collection = self.collectinfos(module, patterns)
    printer = self.nameprinterclass()
    output = printer.print_(collection = collection)
    return output

  # ---------------------------------------------------------------------------
  def getsuite(self, module, patterns = None):
    collection = self.collectinfos(module, patterns)
    suitefactory = self.suitefactoryclass()
    suite = suitefactory.build(collection = collection)
    return suite

  # ---------------------------------------------------------------------------
  def runtests(self, module, patterns, verbosity):
    suite = self.getsuite(module, patterns)
    runner = self.runnerclass()
    output, result = runner.run(suite = suite, verbosity = verbosity)
    return output, result

# =============================================================================
class Main(object):
  default = object()
  defaultworkerclass = Worker

  # ---------------------------------------------------------------------------
  def __init__(self, worker = default):
    if worker is self.default:
      worker = self.defaultworkerclass()
    self.worker = worker

  # ---------------------------------------------------------------------------
  def getopt(self, argv):
    shortopts = 'hqvdl'
    longopts = ['help', 'quiet', 'verbose', 'debug', 'list']
    try:
      opts, args = getopt.getopt(argv, shortopts, longopts)
    except getopt.GetoptError as error:
      message, option = error.args
      raise ArgvError(message, option)
    return opts, args

  # ---------------------------------------------------------------------------
  def parsegetopt(self, opts, args):
    options = {}
    for opt, _ in opts:
      if opt in ('-h', '--help'):
        options['help'] = True
      elif opt in ('-q', '--quiet'):
        options['verbosity'] = 0
      elif opt in ('-v', '--verbose'):
        options['verbosity'] = 2
      elif opt in ('-d', '--debug'):
        options['debug'] = True
      elif opt in ('-l', '--list'):
        options['action'] = 'printname'
      else:
        raise Error('unknown option: %s' % opt) # pragma: no cover
    if args:
      options['patterns'] = args
    return options

  # ---------------------------------------------------------------------------
  def getoptions(self, argv):
    opts, args = self.getopt(argv)
    options = {
          'help': False,
          'verbosity': 1,
          'debug': False,
          'action': 'runtests',
          'patterns': None}
    parsedoptions = self.parsegetopt(opts, args)
    options.update(parsedoptions)
    return options

  # ---------------------------------------------------------------------------
  def printname(self, options, module):
    output = self.worker.printname(module, options['patterns'])
    return output, 0

  # ---------------------------------------------------------------------------
  def runtests(self, options, module):
    output, result = self.worker.runtests(module, options['patterns'],
          options['verbosity'])
    exitstatus = self.getexitstatus(result)
    return output, exitstatus

  # ---------------------------------------------------------------------------
  def getexitstatus(self, result):
    if result:
      exitstatus = 0
    else:
      exitstatus = 1
    return exitstatus

  # ---------------------------------------------------------------------------
  def dowork(self, options, module):
    action = options['action']
    if action == 'printname':
      output, exitstatus = self.printname(options, module)
    elif action == 'runtests':
      output, exitstatus = self.runtests(options, module)
    else:
      raise Error('unknown action: %s' % action) # pragma: no cover
    return output, exitstatus

  # ---------------------------------------------------------------------------
  def runexcept(self, argv, module):
    options = self.getoptions(argv)
    output, exitstatus = self.dowork(options, module)
    return output, exitstatus

  # ---------------------------------------------------------------------------
  def run(self, argv, module):
    try:
      output, exitstatus = self.runexcept(argv, module)
    except (ArgvError, FilterError) as error:
      output = 'ERROR: %s\n' % str(error)
      exitstatus = 2
    except Exception as error:
      output = 'ERROR: %s\n' % str(error)
      exitstatus = 3
    return output, exitstatus

# =============================================================================
def main(module = None, argv = None): # pragma: no cover
  if module is None:
    module = __import__('__main__')
  if argv is None:
    argv = sys.argv[1:]
  mainobject = Main()
  output, exitstatus = mainobject.run(argv, module)
  sys.stdout.write(output)
  sys.exit(exitstatus)

# =============================================================================
class TestLoader(object):
  default = object()
  defaultworkerclass = Worker

  # ---------------------------------------------------------------------------
  def __init__(self, worker = default):
    if worker is self.default:
      worker = self.defaultworkerclass()
    self.worker = worker

  # ---------------------------------------------------------------------------
  def loadTestsFromModule(self, module):
    # ignore camel case names: pylint: disable=C0103
    suite = self.worker.getsuite(module)
    return suite

  # ---------------------------------------------------------------------------
  def loadTestsFromNames(self, patterns, module = None):
    # ignore camel case names: pylint: disable=C0103
    suite = self.worker.getsuite(module, patterns)
    return suite
