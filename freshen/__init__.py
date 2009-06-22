__all__ = ['Given', 'When', 'Then', 'And', 'Before', 'After', 'AfterStep', 'run_steps', 'glc', 'scc']

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

# Contexts
class Context(object):
    """
    A javascript/lua like dictionary whose items can be accessed as attributes
    """
    
    def __init__(self):
        self.__dict__['d'] = {}
    
    def __getattr__(self, name):
        if name in self.d:
            return self.d[name]
        else:
            return None
    __getitem__ = __getattr__
    
    def __setattr__(self, name, value):
        self.d[name] = value
    __setitem__ = __setattr__
    
    def __delattr__(self, name):
        if name in self.d:
            del self.d[name]
    __delitem__ = __delattr__

    def clear(self):
        self.__dict__['d'] = {}


glc = Context() # Global context - never cleared
ftc = Context() # Feature context - cleared for every feature
scc = Context() # Scenario context - cleared for every scenario

def step_decorator(spec):
    """ Decorator to wrap step definitions in. Registers definition. """
    def wrapper(func):
        r = re.compile(spec)
        step_registry['step'][r] = func
        return func
    return wrapper

def hook_decorator(kind):
    """ Decorator to wrap hook definitions in. Registers hook. """
    def decorator_wrapper(*args):
        
        if len(args) == 1 and callable(args[0]):
            # No tags were passed to this decorator
            step_registry[kind].add(args[0])
            return args[0]
        else:
            # We got some tags, so we need to produce the real decorator
            def d(func):
                def func_wrapper(scenario):
                    if scenario.tags_match(args):
                        func(scenario)

                step_registry[kind].add(func_wrapper)
                return func_wrapper
            return d
    return decorator_wrapper

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


def tags_match(mytags, include, exclude):
    if set(mytags) & set(exclude):
        return False
    
    return not include or (set(mytags) & set(include))


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

class FeatureSuite(object):

    def setUp(self):
        #log.debug("Clearing feature context")
        ftc.clear()

class FreshenTestCase(unittest.TestCase):

    def __init__(self, feature, scenario, feature_suite):
        self.feature = feature
        self.scenario = scenario
        self.context = feature_suite
        
        self.description = feature.name + ": " + scenario.name
        super(FreshenTestCase, self).__init__()
    
    def setUp(self):
        #log.debug("Clearing scenario context")
        scc.clear()
        for func in step_registry['before']:
            func(self.scenario)
    
    def runTest(self):
        for step in self.scenario.steps:
            res = find_and_run_match(step)
            for func in step_registry['after_step']:
                func(self.scenario)
    
    def tearDown(self):
        for func in step_registry['after']:
            func(self.scenario)

definition_paths = []

def load_feature(fname):
    """ Load and parse a feature file. """

    fname = os.path.abspath(fname)
    path = os.path.dirname(fname)
    
    feat = parser.parse_file(fname)

    if path not in definition_paths:
        try:
            info = imp.find_module("steps", [path])
            mod = imp.load_module("steps", *info)
            definition_paths.append(path)
        except ImportError:
            pass
    
    return feat

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
    
    def options(self, parser, env):
        super(FreshenNosePlugin, self).options(parser, env)
        
        parser.add_option('--tags', action='store',
                          dest='tags',
                          default=env.get('NOSE_FRESHEN_TAGS'),
                          help="Run only those scenarios and features which "
                               "match the given tags. Should be a comma-separated "
                               "list. Each tag can be prefixed with a ~ to negate "
                               "[NOSE_FRESHEN_TAGS]")

    def configure(self, options, config):
        super(FreshenNosePlugin, self).configure(options, config)
        all_tags = options.tags.split(",") if options.tags else []
        self.include_tags = [t.lstrip("@") for t in all_tags if not t.startswith("~")]
        self.exclude_tags = [t.lstrip("~@") for t in all_tags if t.startswith("~")]
    
    def wantDirectory(self, dirname):
        if not os.path.exists(os.path.join(dirname, ".freshenignore")):
            return True
        return None
    
    def wantFile(self, filename):
        return filename.endswith(".feature") or None
    
    def loadTestsFromFile(self, filename, indexes=[]):
        log.debug("Loading from file %s" % filename)
        try:
            feat = load_feature(filename)
        except ParseException, e:
            ec, ev, tb = sys.exc_info()
            yield Failure(ParseException, ParseException(e.pstr, e.loc, e.msg + " in %s" % filename), tb)
            return
        
        cnt = 0
        ctx = FeatureSuite()
        for i, sc in enumerate(feat.iter_scenarios()):
            if (not indexes or (i + 1) in indexes):
                if tags_match(sc.tags + feat.tags, self.include_tags, self.exclude_tags):
                    yield FreshenTestCase(feat, sc, ctx)
                    cnt += 1
        
        if not cnt:
            yield False
    
    def loadTestsFromName(self, name, _=None):
        log.debug("Loading from name %s" % name)
        
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
        if hasattr(test, 'test') and isinstance(test.test, FreshenTestCase):
            ec, ev, tb = err
            if ec is ExceptionWrapper:
                orig_ec, orig_ev, orig_tb = ev.e
                return (orig_ec, str(orig_ev) + "\n\n>> in " + format_step(ev.step), orig_tb)
            else:
                return err
    
    formatError = formatFailure

