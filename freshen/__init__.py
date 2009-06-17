__all__ = ['Given', 'When', 'Then', 'load_feature']

import imp
import os
import re
import parser
import traceback
import logging
import unittest
from nose.plugins import Plugin
from nose.plugins.skip import SkipTest
from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin


from freshen.parser import Step

spec_registry = {}

def step(spec):
    def wrapper(func):
        r = re.compile(spec)
        spec_registry[r] = func
        return func
    return wrapper

Given = step
When = step
Then = step

log = logging.getLogger('nose.plugins')

class FreshenException(Exception):
    pass

class UndefinedStep(Exception):
    
    def __init__(self, step):
        p = os.path.relpath(step.src_file, os.getcwd())
        super(UndefinedStep, self).__init__(
            '"%s" # %s:%d' % (step.match,
                            p,
                            step.src_line))

def find_and_run_match(step):
    result = None
    for r, f in spec_registry.iteritems():
        matches = r.match(step.match)
        if matches:
            if result:
                raise FreshenException("Ambiguous: %s" % step.match)
            result = f, matches
    
    if not result:
        raise UndefinedStep(step)
    return result[0](*result[1].groups())


class FreshenTestCase(unittest.TestCase):

    def __init__(self, feature, scenario, before, after):
        self.feature = feature
        self.scenario = scenario
        self.before = before
        self.after = after
        
        self.description = feature.name + ": " + scenario.name
        super(FreshenTestCase, self).__init__()
    
    def setUp(self):
        if self.before:
            self.before()
    
    def runTest(self):
        for step in self.scenario.steps:
            res = find_and_run_match(step)
    
    def tearDown(self):
        if self.after:
            self.after()

def load_feature(fname):
    fname = os.path.abspath(fname)
    path = os.path.dirname(fname)
    
    before = after = None
    try:
        info = imp.find_module("steps", [path])
        mod = imp.load_module("steps", *info)

        before = getattr(mod, 'before', None)
        after = getattr(mod, 'after', None)
    except ImportError:
        pass
    
    return parser.parse_file(fname), before, after


class FreshenErrorPlugin(ErrorClassPlugin):

    enabled = True
    undefined = ErrorClass(UndefinedStep,
                           label="UNDEFINED",
                           isfailure=False)

    def options(self, parser, env):
        # Forced to be on!
        pass


class FreshenNosePlugin(Plugin):
    
    name = "freshen"
    
    def wantDirectory(self, dirname):
        return True
    
    def wantFile(self, filename):
        return filename.endswith(".feature")
    
    def loadTestsFromFile(self, filename):
        feat, before, after = load_feature(filename)
        
        for sc in feat.iter_scenarios():
            yield FreshenTestCase(feat, sc, before, after)
    
    def describeTest(self, test):
        if isinstance(test.test, FreshenTestCase):
            return test.test.description


