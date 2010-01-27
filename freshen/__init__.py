#-*- coding: utf8 -*-
__all__ = ['Given', 'When', 'Then', 'And', 'Before', 'After', 'AfterStep', 'glc', 'scc']

import imp
import inspect
import os
import re
import parser
import traceback
import unittest
import sys
import types
import yaml
from nose.plugins import Plugin
from nose.plugins.skip import SkipTest
from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from nose.selector import TestAddress
from nose.failure import Failure
from freshen import parser
from freshen.stepsregistry import StepImplRegistry, AmbiguousStepImpl, UndefinedStepImpl
from freshen.stepsregistry import *
from pyparsing import ParseException

try:
    from os.path import relpath
except Exception, e:
    from compat import relpath

import logging
log = logging.getLogger('nose.plugins.freshen')

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1

class TagMatcher(object):
    
    def __init__(self, tags):
        self.include_tags = set(t.lstrip("@") for t in tags if not t.startswith("~"))
        self.exclude_tags = set(t.lstrip("~@") for t in tags if t.startswith("~"))

    def check_match(self, tagset):
        tagset = set(t.lstrip("@") for t in tagset)
        if tagset & self.exclude_tags:
            return False
        
        return not self.include_tags or (tagset & self.include_tags)

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

# --- Internals ---

class StepsRunner(object):
    
    def __init__(self, step_registry):
        self.step_registry = step_registry
    
    def run_steps_from_string(self, spec, language_name='en'):
        """ Called from within step definitions to run other steps. """
        
        caller = inspect.currentframe().f_back
        line = caller.f_lineno - 1
        fname = caller.f_code.co_filename
        
        steps = parser.parse_steps(spec, fname, line, load_language(language_name))
        for s in steps:
            self.run_step(s)
    
    def run_step(self, step):
        step_impl, args = self.step_registry.find_step_impl(step.match)
        try:
            if step.arg is not None:
                return step_impl.func(self, step.arg, *args)
            else:
                return step_impl.func(self, *args)
        except (UndefinedStepImpl, AssertionError, ExceptionWrapper):
            raise
        except Exception, e:
            raise ExceptionWrapper(sys.exc_info(), step)

class FreshenException(Exception):
    pass

class ExceptionWrapper(Exception):
    
    def __init__(self, e, step):
        self.e = e
        self.step = step

def format_step(step):
    p = relpath(step.src_file, os.getcwd())
    return '"%s" # %s:%d' % (step.match,
                             p,
                             step.src_line)


class FeatureSuite(object):

    def setUp(self):
        #log.debug("Clearing feature context")
        ftc.clear()

class FreshenTestCase(unittest.TestCase):

    start_live_server = True
    database_single_transaction = True
    database_flush = True
    selenium_start = False
    no_database_interaction = False
    make_translations = True
    required_sane_plugins = ["django", "http"]    
    django_plugin_started = False
    http_plugin_started = False
    
    test_type = "http"

    def __init__(self, step_runner, step_registry, feature, scenario, feature_suite):
        self.feature = feature
        self.scenario = scenario
        self.context = feature_suite
        self.step_registry = step_registry
        self.step_runner = step_runner
        
        self.description = feature.name + ": " + scenario.name
        super(FreshenTestCase, self).__init__()
    
    def setUp(self):
        #log.debug("Clearing scenario context")
        scc.clear()
        for func in self.step_registry.get_hooks('before', self.scenario.get_tags()):
            func(self.step_runner, self.scenario)
    
    def runTest(self):
        for step in self.scenario.steps:
            self.step_runner.run_step(step)
            for func in self.step_registry.get_hooks('after_step', self.scenario.get_tags()):
                func(self.step_runner, self.scenario)
    
    def tearDown(self):
        for func in self.step_registry.get_hooks('after', self.scenario.get_tags()):
            func(self.step_runner, self.scenario)


def load_feature(step_registry, fname, language):
    """ Load and parse a feature file. """

    fname = os.path.abspath(fname)
    path = os.path.dirname(fname)
    feat = parser.parse_file(fname, language)
    step_registry.load_steps_impl(path)
    return feat

class Language(object):
    def __init__(self, mappings):
        self.mappings = mappings
    
    def word(self, key):
        return self.mappings[key].encode('utf')

def load_language(language_name):
    directory, _f = os.path.split(os.path.abspath(__file__))
    languages = yaml.load(open(os.path.join(directory, 'languages.yml')))
    if language_name not in languages:
        return None
    return Language(languages[language_name])


class FreshenErrorPlugin(ErrorClassPlugin):

    enabled = True
    undefined = ErrorClass(UndefinedStepImpl,
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
        parser.add_option('--language', action="store", dest='language',
            default='en',
            help='Change the language used when reading the feature files',
        )

    def configure(self, options, config):
        super(FreshenNosePlugin, self).configure(options, config)
        all_tags = options.tags.split(",") if options.tags else []
        self.tagmatcher = TagMatcher(all_tags)
        self.language = load_language(options.language)
        self.step_registry = StepImplRegistry(TagMatcher)
        if not self.language:
            print >> sys.stderr, "Error: language '%s' not available" % options.language
            exit(1)
    
    def wantDirectory(self, dirname):
        if not os.path.exists(os.path.join(dirname, ".freshenignore")):
            return True
        return None
    
    def wantFile(self, filename):
        return filename.endswith(".feature") or None
    
    def loadTestsFromFile(self, filename, indexes=[]):
        log.debug("Loading from file %s" % filename)
        try:
            feat = load_feature(self.step_registry, filename, self.language)
        except ParseException, e:
            ec, ev, tb = sys.exc_info()
            yield Failure(ParseException, ParseException(e.pstr, e.loc, e.msg + " in %s" % filename), tb)
            return
        
        cnt = 0
        ctx = FeatureSuite()
        for i, sc in enumerate(feat.iter_scenarios()):
            if (not indexes or (i + 1) in indexes):
                if self.tagmatcher.check_match(sc.tags + feat.tags):
                    yield FreshenTestCase(StepsRunner(self.step_registry), self.step_registry, feat, sc, ctx)
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
            if ec is ExceptionWrapper and isinstance(ev, Exception):
                orig_ec, orig_ev, orig_tb = ev.e
                return (orig_ec, str(orig_ev) + "\n\n>> in " + format_step(ev.step), orig_tb)
            else:
                return err
    
    formatError = formatFailure

