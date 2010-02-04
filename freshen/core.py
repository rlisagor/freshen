import os
from freshen import *
from freshen import TagMatcher, load_feature, load_language, StepsRunner
from freshen.stepregistry import StepImplRegistry

class FreshenHandler(object):
    
    def before_feature(self, feature):
        print "before feature", feature
    
    def after_feature(self, feature):
        print "after feature", feature
    
    def before_scenario(self, scenario):
        print "    before scenario", scenario
    
    def after_scenario(self, scenario):
        print "    after scenario", scenario

    def before_step(self, step):
        print "        before step", step

    def after_step(self, step):
        print "        after step", step

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
        runner.run_step(step)
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

def load_features(paths, language):
    result = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for feature_file in filenames:
                if feature_file.endswith(".feature"):
                    feature_file = os.path.join(dirpath, feature_file)
                    result.append(load_feature(feature_file, language))
    return result

def load_steps(paths):
    sr = StepImplRegistry(TagMatcher)
    for path in paths:
        sr.load_steps_impl(path)
    return sr

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    paths = sys.argv[1:] or ["features"]
    
    language = load_language('en')
    registry = load_steps(paths)
    features = load_features(paths, language)
    handler = FreshenHandler()
    run_features(registry, features, handler)
