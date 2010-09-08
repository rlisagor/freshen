#!/usr/bin/env python

import sys
from os import listdir
from os.path import dirname, relpath, isdir, join

from freshen.core import TagMatcher, load_language, load_feature
from freshen.stepregistry import StepImplLoader, StepImplRegistry, UndefinedStepImpl



LANGUAGE = 'en'

class Colors(object):
    HEADER = '\033[95m'
    FILE = '\033[93m'
    ENDC = '\033[0m'

    @classmethod
    def disable(cls):
        cls.HEADER = ''
        cls.FILE = ''
        cls.ENDC = ''

    @classmethod
    def write(cls, text, color):
        return "%s%s%s" % (color, text, cls.ENDC)



def load_file(filepath):
    feature = load_feature(filepath, load_language(LANGUAGE))
    registry = StepImplRegistry(TagMatcher)
    loader = StepImplLoader()
    loader.load_steps_impl(registry, dirname(feature.src_file), feature.use_step_defs)
    return registry

def load_dir(dirpath):
    registry = StepImplRegistry(TagMatcher)
    loader = StepImplLoader()
    def walktree(top, filter_func=lambda x: True):
        names = listdir(top)
        for name in names:
            path = join(top, name)
            if filter_func(path):
                yield path
            if isdir(path):
                for i in walktree(path, filter_func):
                    yield i
    for feature_file in walktree(dirpath, lambda x: x.endswith('.feature')):
        feature = load_feature(feature_file, load_language(LANGUAGE))
        loader.load_steps_impl(registry, dirname(feature.src_file), feature.use_step_defs)
    return registry

def print_registry(registry):
    steps = {}
    for keyword in ['given', 'when', 'then']:
        steps[keyword] = {}
        for step in registry.steps[keyword]:
            path = relpath(step.get_location())
            filename = path.rsplit(':', 1)[0]
            if filename not in steps[keyword]:
                steps[keyword][filename] = []
            if step not in steps[keyword][filename]:
                steps[keyword][filename].append(step)
    for keyword in ['given', 'when', 'then']:
        print Colors.write(keyword.upper(), Colors.HEADER)
        for filename in steps[keyword]:
            print "  %s" % Colors.write(filename, Colors.FILE)
            for step in steps[keyword][filename]:
                print "    %s" % step.spec


def list_steps():
    file_or_dir = sys.argv[1]
    if isdir(file_or_dir):
        registry = load_dir(file_or_dir)
    else:
        registry = load_file(file_or_dir)
    print_registry(registry)

