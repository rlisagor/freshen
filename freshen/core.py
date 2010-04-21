#-*- coding: utf8 -*-

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1

import inspect
import os
import yaml

from freshen.context import *
from freshen.parser import parse_steps, parse_file
from freshen.stepregistry import StepImplRegistry, UndefinedStepImpl, AmbiguousStepImpl


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
            return step_impl.run(step.arg, *args)
        else:
            return step_impl.run(*args)


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

def load_feature(fname, language):
    """ Load and parse a feature file. """

    fname = os.path.abspath(fname)
    feat = parse_file(fname, language)
    return feat

def load_language(language_name):
    directory, _f = os.path.split(os.path.abspath(__file__))
    languages = yaml.load(open(os.path.join(directory, 'languages.yml')))
    if language_name not in languages:
        return None
    return Language(languages[language_name])

def run_steps(spec, language="en"):
    """ Can be called by the user from within a step definition to execute other steps. """

    # The way this works is a little exotic, but I couldn't think of a better way to work around
    # the fact that this has to be a global function and therefore cannot know about which step
    # runner to use (other than making step runner global)
    
    # Find the step runner that is currently running and use it to run the given steps
    fr = inspect.currentframe()
    while fr:
        if "self" in fr.f_locals:
            f_self = fr.f_locals['self']
            if isinstance(f_self, StepsRunner):
                return f_self.run_steps_from_string(spec, language)
        fr = fr.f_back



