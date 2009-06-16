__all__ = ['Given', 'When', 'Then', 'load_feature']

import imp
import os
import re
import parser
import traceback
import nose.plugins
import logging
import unittest

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

def find_and_run_match(s):
    result = None
    for r, f in spec_registry.iteritems():
        matches = r.match(s)
        if matches:
            if result:
                raise Exception("Ambiguous: %s" % s)
            result = f, matches
    
    if not result:
        raise Exception("Could not match to definition: %s" % s)
    return result[0](*result[1].groups())


class FreshenTestCase(unittest.TestCase):
    
    def __init__(self, scenario, before, after):
        self.scenario = scenario
        self.before = before
        self.after = after
        super(FreshenTestCase, self).__init__()
    
    def setUp(self):
        if self.before:
            self.before()
    
    def runTest(self):
        for step in self.scenario.steps:
            res = find_and_run_match(step.match)

    def tearDown(self):
        if self.after:
            self.after()

def load_feature(fname):
    fname = os.path.abspath(fname)
    path = os.path.dirname(fname)
    
    info = imp.find_module("steps", [path])
    mod = imp.load_module("steps", *info)

    before = getattr(mod, 'before', None)
    after = getattr(mod, 'after', None)
    return parser.parse_file(fname), before, after


class FreshenNosePlugin(nose.plugins.Plugin):
    
    name = "freshen"
    
    def wantDirectory(self, dirname):
        return True
    
    def wantFile(self, filename):
        return filename.endswith(".feature")
    
    def loadTestsFromFile(self, filename):
        feat, before, after = load_feature(filename)
        
        for sc in feat.iter_scenarios():
            yield FreshenTestCase(sc, before, after)



