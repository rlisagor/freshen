#-*- coding: utf8 -*-

# Experimental - a non-nose runner for tests, may end up being compatible
# with Cucumber commandline

import os
from freshen.context import *
from freshen.core import TagMatcher, StepsRunner, load_feature, load_language
from freshen.stepregistry import StepImplLoader, StepImplRegistry, UndefinedStepImpl, AmbiguousStepImpl

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


def run_scenario(step_registry, scenario, handler):
    handler.before_scenario(scenario)
    
    runner = StepsRunner(step_registry)
    scc.clear()
    
    # Run @Before hooks
    for hook_impl in step_registry.get_hooks('before', scenario.get_tags()):
        hook_impl.run(scenario)
    
    # Run all the steps
    for step in scenario.iter_steps():
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
        hook_impl.run(scenario)    
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

def load_step_definitions(paths):
    loader = StepImplLoader()
    sr = StepImplRegistry(TagMatcher)
    for path in paths:
        loader.load_steps_impl(sr, path)
    return sr

def load_features(paths, language):
    result = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for feature_file in filenames:
                if feature_file.endswith(".feature"):
                    feature_file = os.path.join(dirpath, feature_file)
                    result.append(load_feature(feature_file, language))
    return result

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

