__all__ = ['Given', 'When', 'Then', 'And', 'Before', 'After', 'AfterStep', 'run_steps']

import imp
import inspect
import os
import re
import parser
import traceback
import unittest
import sys
import types
from nose.plugins import Plugin
from nose.plugins.skip import SkipTest
from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from nose.selector import TestAddress
from nose.failure import Failure
from freshen import parser
from pyparsing import ParseException

import logging
log = logging.getLogger('nose.plugins')

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1

# Step definitions and hooks collect here
step_registry = {
    'before': set(),
    'after': set(),
    'after_step': set(),
    'step': {}
}

# --- Functions available to step definitions files ---

def step_decorator(spec):
    """ Decorator to wrap step definitions in. Registers definition. """
    def wrapper(func):
        r = re.compile(spec)
        step_registry['step'][r] = func
        return func
    return wrapper

def hook_decorator(kind):
    """ Decorator to wrap hook definitions in. Registers hook. """
    def wrapper(func):
        step_registry[kind].add(func)
        return func
    return wrapper

Given = When = Then = And = step_decorator
Before = hook_decorator('before')
After = hook_decorator('after')
AfterStep = hook_decorator('after_step')

def run_steps(spec):
    """ Called from within step definitions to run other steps. """
    
    caller = inspect.currentframe().f_back
    line = caller.f_lineno - 1
    fname = caller.f_code.co_filename
    
    steps = parser.parse_steps(spec, fname, line)
    
    for s in steps:
        find_and_run_match(s)

# --- Internals ---

class FreshenException(Exception):
    pass

class ExceptionWrapper(Exception):
    
    def __init__(self, e, step):
        self.e = e
        self.step = step

def format_step(step):
    p = os.path.relpath(step.src_file, os.getcwd())
    return '"%s" # %s:%d' % (step.match,
                             p,
                             step.src_line)

class UndefinedStep(Exception):
    
    def __init__(self, step):
        p = os.path.relpath(step.src_file, os.getcwd())
        super(UndefinedStep, self).__init__(format_step(step))

def find_and_run_match(step):
    """ Look up the step in the registry, then run it """
    result = None
    for r, f in step_registry['step'].iteritems():
        matches = r.match(step.match)
        if matches:
            if result:
                raise FreshenException("Ambiguous: %s" % step.match)
            result = f, matches
    
    if not result:
        raise UndefinedStep(step)
        
    try:
        if step.arg is not None:
            return result[0](step.arg, *result[1].groups())
        else:
            return result[0](*result[1].groups())
    except (UndefinedStep, ExceptionWrapper):
        raise
    except Exception, e:
        raise ExceptionWrapper(sys.exc_info(), step)


class FreshenTestCase(unittest.TestCase):

    def __init__(self, feature, scenario):
        self.feature = feature
        self.scenario = scenario
        
        self.description = feature.name + ": " + scenario.name
        super(FreshenTestCase, self).__init__()
    
    def setUp(self):
        for func in step_registry['before']:
            func()
    
    def runTest(self):
        for step in self.scenario.steps:
            res = find_and_run_match(step)
            for func in step_registry['after_step']:
                func()
    
    def tearDown(self):
        for func in step_registry['after']:
            func()

def load_feature(fname):
    """ Load and parse a feature file. """

    fname = os.path.abspath(fname)
    path = os.path.dirname(fname)
    
    try:
        info = imp.find_module("steps", [path])
        mod = imp.load_module("steps", *info)
    except ImportError:
        pass
    
    return parser.parse_file(fname)

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
    
    def loadTestsFromFile(self, filename, indexes=[]):
        try:
            feat = load_feature(filename)
        except ParseException, e:
            ec, ev, tb = sys.exc_info()
            yield Failure(ParseException, ParseException(e.pstr, e.loc, e.msg + " in %s" % filename), tb)
            return
        
        for i, sc in enumerate(feat.iter_scenarios()):
            if not indexes or (i + 1) in indexes:
                yield FreshenTestCase(feat, sc)
    
    def loadTestsFromName(self, name, _=None):
        log.debug("Loading from name %r" % name)
        indexes = []
        if ":" not in name:
            # let nose take care of it
            return
        
        parts = name.split(":")
        name = parts.pop(0)
        indexes = set(int(p) for p in parts)
        
        if not os.path.exists(name):
            return
        
        if os.path.isfile(name) and name.endswith(".feature"):
            for tc in self.loadTestsFromFile(name, indexes):
                yield tc
    
    def describeTest(self, test):
        if isinstance(test.test, FreshenTestCase):
            return test.test.description

    def formatFailure(self, test, err):
        if isinstance(test.test, FreshenTestCase):
            ec, ev, tb = err
            if ec is ExceptionWrapper:
                orig_ec, orig_ev, orig_tb = ev.e
                return (orig_ec, str(orig_ev) + "\n\n>> in " + format_step(ev.step), orig_tb)
            else:
                return err
    
    formatError = formatFailure

