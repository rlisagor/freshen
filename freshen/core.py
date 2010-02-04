#-*- coding: utf8 -*-

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1

import inspect
import os
import yaml

from freshen.context import *
from freshen.parser import parse_steps, parse_file
from freshen.stepregistry import StepImplRegistry, UndefinedStepImpl, AmbiguousStepImpl


class FreshenHandler(object):
    
    def before_feature(self, feature):
        pass
    
    def after_feature(self, feature):
        pass
    
    def before_scenario(self, scenario):
        pass
    
    def after_scenario(self, scenario):
        pass

    def before_step(self, step):
        pass
    
    def step_failed(self, step, e):
        pass
    
    def step_ambiguous(self, step, e):
        pass
        
    def step_undefined(self, step, e):
        pass
    
    def step_exception(self, step, e):
        pass
    
    def after_step(self, step):
        pass


class FreshenHandlerProxy(object):
    """ Acts as a handler and proxies callback events to a list of actual handlers. """
        
    def __init__(self, handlers):
        self._handlers = handlers
    
    def __getattr__(self, attr):
        def proxy(*args, **kwargs):
            for h in self._handlers:
                method = getattr(h, attr)
                method(*args, **kwargs)
        return proxy


class StepsRunner(object):
    
    def __init__(self, step_registry):
        self.step_registry = step_registry
    
    def run_steps_from_string(self, spec, language_name='en'):
        """ Called from within step definitions to run other steps. """
        
        caller = inspect.currentframe().f_back
        line = caller.f_lineno - 1
        fname = caller.f_code.co_filename
        
        steps = parse_steps(spec, fname, line, load_language(language_name))
        for s in steps:
            self.run_step(s)
    
    def run_step(self, step):
        step_impl, args = self.step_registry.find_step_impl(step)
        if step.arg is not None:
            return step_impl.run(self, step.arg, *args)
        else:
            return step_impl.run(self, *args)


class TagMatcher(object):
    
    def __init__(self, tags):
        self.include_tags = set(t.lstrip("@") for t in tags if not t.startswith("~"))
        self.exclude_tags = set(t.lstrip("~@") for t in tags if t.startswith("~"))

    def check_match(self, tagset):
        tagset = set(t.lstrip("@") for t in tagset)
        if tagset & self.exclude_tags:
            return False
        
        return not self.include_tags or (tagset & self.include_tags)


class Language(object):
    def __init__(self, mappings):
        self.mappings = mappings
    
    def word(self, key):
        return self.mappings[key].encode('utf')

def run_scenario(step_registry, scenario, handler):
    handler.before_scenario(scenario)
    
    runner = StepsRunner(step_registry)
    scc.clear()
    
    # Run @Before hooks
    for hook_impl in step_registry.get_hooks('before', scenario.get_tags()):
        hook_impl.run(runner, scenario)
    
    # Run all the steps
    for step in scenario.steps:
        handler.before_step(step)
        
        called = False
        try:
            runner.run_step(step)
        except AssertionError, e:
            handler.step_failed(step, e)
            called = True
        except UndefinedStepImpl, e:
            handler.step_undefined(step, e)
            called = True
        except AmbiguousStepImpl, e:
            handler.step_ambiguous(step, e)
            called = True
        except Exception, e:
            handler.step_exception(step, e)
            called = True
        
        if not called:
            handler.after_step(step)
    
    # Run @After hooks
    for hook_impl in step_registry.get_hooks('after', scenario.get_tags()):
        hook_impl.run(runner, scenario)    
    handler.after_scenario(scenario)

def run_feature(step_registry, feature, handler):
    handler.before_feature(feature)
    ftc.clear()
    for scenario in feature.iter_scenarios():
        run_scenario(step_registry, scenario, handler)
    handler.after_feature(feature)

def run_features(step_registry, features, handler):
    for feature in features:
        run_feature(step_registry, feature, handler)


def load_feature(fname, language):
    """ Load and parse a feature file. """

    fname = os.path.abspath(fname)
    feat = parse_file(fname, language)
    return feat

def load_features(paths, language):
    result = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for feature_file in filenames:
                if feature_file.endswith(".feature"):
                    feature_file = os.path.join(dirpath, feature_file)
                    result.append(load_feature(feature_file, language))
    return result

def load_step_definitions(paths):
    sr = StepImplRegistry(TagMatcher)
    for path in paths:
        sr.load_steps_impl(path)
    return sr

def load_language(language_name):
    directory, _f = os.path.split(os.path.abspath(__file__))
    languages = yaml.load(open(os.path.join(directory, 'languages.yml')))
    if language_name not in languages:
        return None
    return Language(languages[language_name])


if __name__ == "__main__":
    import sys
    import logging
    from freshen.handlers import ConsoleHandler
    
    logging.basicConfig(level=logging.DEBUG)
    
    paths = sys.argv[1:] or ["features"]
    
    language = load_language('en')
    registry = load_step_definitions(paths)
    features = load_features(paths, language)
    handler = FreshenHandlerProxy([ConsoleHandler()])
    run_features(registry, features, handler)

