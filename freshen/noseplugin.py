#-*- coding: utf8 -*-

import unittest
import sys
import os
import logging

from pyparsing import ParseException

from nose.plugins import Plugin
from nose.plugins.skip import SkipTest
from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from nose.selector import TestAddress
from nose.failure import Failure

from freshen.core import TagMatcher, load_language, load_feature, StepsRunner
from freshen.context import *
from freshen.stepregistry import StepImplLoader, StepImplRegistry, UndefinedStepImpl

log = logging.getLogger('nose.plugins.freshen')

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1

class ExceptionWrapper(Exception):
    
    def __init__(self, e, step):
        self.e = e
        self.step = step

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
        for hook_impl in self.step_registry.get_hooks('before', self.scenario.get_tags()):
            hook_impl.run(self.scenario)
    
    def runTest(self):
        for step in self.scenario.iter_steps():
            try:
                self.step_runner.run_step(step)
            except (AssertionError, UndefinedStepImpl, ExceptionWrapper):
                raise
            except:
                raise ExceptionWrapper(sys.exc_info(), step)
            
            for hook_impl in reversed(self.step_registry.get_hooks('after_step', self.scenario.get_tags())):
                hook_impl.run(self.scenario)
    
    def tearDown(self):
        for hook_impl in reversed(self.step_registry.get_hooks('after', self.scenario.get_tags())):
            hook_impl.run(self.scenario)


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
        self.impl_loader = StepImplLoader()
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
        
        step_registry = StepImplRegistry(TagMatcher)
        try:
            feat = load_feature(filename, self.language)
            path = os.path.dirname(filename)
            self.impl_loader.load_steps_impl(step_registry, path, feat.use_step_defs)
        except ParseException, e:
            ec, ev, tb = sys.exc_info()
            yield Failure(ParseException, ParseException(e.pstr, e.loc, e.msg + " in %s" % filename), tb)
            return
        
        cnt = 0
        ctx = FeatureSuite()
        for i, sc in enumerate(feat.iter_scenarios()):
            if (not indexes or (i + 1) in indexes):
                if self.tagmatcher.check_match(sc.tags + feat.tags):
                    yield FreshenTestCase(StepsRunner(step_registry), step_registry, feat, sc, ctx)
                    cnt += 1
        
        if not cnt:
            yield False
    
    def loadTestsFromName(self, name, _=None):
        log.debug("Loading from name %s" % name)
        
        if not self._is_file_with_indexes(name):
            return # let nose take care of it
            
        name_without_indexes, indexes = self._split_file_in_indexes(name)
        
        if not os.path.exists(name_without_indexes):
            return
        
        if os.path.isfile(name_without_indexes) \
           and name_without_indexes.endswith(".feature"):
            for tc in self.loadTestsFromFile(name_without_indexes, indexes):
                yield tc
                
    def _is_file_with_indexes(self, name):
        drive, tail = os.path.splitdrive(name)
        if ":" not in tail:
            return False
        else:
            return True
        
    def _split_file_in_indexes(self, name_with_indexes):
        drive, tail = os.path.splitdrive(name_with_indexes)
        parts = tail.split(":")
        name_without_indexes = drive + parts.pop(0)
        indexes = []
        indexes = set(int(p) for p in parts)
        return (name_without_indexes, indexes)
        
    def describeTest(self, test):
        if isinstance(test.test, FreshenTestCase):
            return test.test.description

    def formatFailure(self, test, err):
        if hasattr(test, 'test') and isinstance(test.test, FreshenTestCase):
            ec, ev, tb = err
            if ec is ExceptionWrapper and isinstance(ev, Exception):
                orig_ec, orig_ev, orig_tb = ev.e
                return (orig_ec, str(orig_ev) + '\n\n>> in "%s" # %s' % (ev.step.match, ev.step.source_location()), orig_tb)
    
    formatError = formatFailure


