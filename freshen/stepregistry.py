#-*- coding: utf8 -*-
import imp
import logging
import re
import os
import sys
import traceback

__all__ = ['Given', 'When', 'Then', 'And', 'Before', 'After', 'AfterStep']
__unittest = 1

log = logging.getLogger('freshen')

class AmbiguousStepImpl(Exception):
    
    def __init__(self, step, impl1, impl2):
        self.step = step
        self.impl1 = impl1
        self.impl2 = impl2
        super(AmbiguousStepImpl, self).__init__('Ambiguous: "%s"\n %s, %s' % (step.match, impl1, impl2))

class UndefinedStepImpl(Exception):
    
    def __init__(self, step):
        self.step = step
        super(UndefinedStepImpl, self).__init__('"%s" # %s' % (step.match, step.source_location()))

class StepImpl(object):
    
    def __init__(self, spec, func):
        self.spec = spec
        self.func = func
        self.re_spec = re.compile(spec)
    
    def run(self, *args, **kwargs):
        self.func(*args, **kwargs)
    
    def match(self, match):
        return self.re_spec.match(match)

class HookImpl(object):
    
    def __init__(self, cb_type, func, tags=[]):
        self.cb_type = cb_type
        self.tags = tags
        self.func = func
        self.tags = tags
        self.order = 0
    
    def __repr__(self):
        return "<Hook: @%s %s(...)>" % (self.cb_type, self.func.func_name)
    
    def run(self, scenario):
        self.func(scenario)


class StepImplLoader(object):

    def __init__(self):
        self.paths = []
        self.module_counter = 0
    
    def load_steps_impl(self, registry, path):
        """
        Load the step implementations from a python module, named 'steps', found at the given path.
        """
        if path not in self.paths:
            #log.debug("Looking for step defs in %s" % path)
            cwd = os.getcwd()
            if cwd not in sys.path:
                sys.path.append(cwd)
            
            try:
                info = imp.find_module("steps", [path])
            except ImportError:
                return
            
            # Modules have to be loaded with unique names or else problems arise
            mod = imp.load_module("steps" + str(self.module_counter), *info)
            self.module_counter += 1
            self.paths.append(path)
            
            for item_name in dir(mod):
                item = getattr(mod, item_name)
                if isinstance(item, StepImpl):
                    registry.add_step(item)
                elif isinstance(item, HookImpl):
                    registry.add_hook(item.cb_type, item)


class StepImplRegistry(object):
    
    def __init__(self, tag_matcher_class):
        self.steps = []
        self.hooks = {
            'before': [],
            'after': [],
            'after_step': []
        }
        self.tag_matcher_class = tag_matcher_class
    
    def add_step(self, step):
        self.steps.append(step)
    
    def add_hook(self, hook_type, hook):
        self.hooks[hook_type].append(hook)
    
    def find_step_impl(self, step):
        """
        Find the implementation of the step for the given match string. Returns the StepImpl object
        corresponding to the implementation, and the arguments to the step implementation. If no
        implementation is found, raises UndefinedStepImpl. If more than one implementation is
        found, raises AmbiguousStepImpl.
        """
        result = None
        for si in self.steps:
            matches = si.match(step.match)
            if matches:
                if result:
                    raise AmbiguousStepImpl(step, result[0], si)
                result = si, matches.groups()
        
        if not result:
            raise UndefinedStepImpl(step)
        return result
    
    def get_hooks(self, cb_type, tags=[]):
        hooks = [h for h in self.hooks[cb_type] if self.tag_matcher_class(h.tags).check_match(tags)]
        hooks.sort(cmp=lambda x,y: cmp(x.order, y.order))
        return hooks


def step_decorator(spec):
    """ Decorator to wrap step definitions in. Registers definition. """
    def wrapper(func):
        return StepImpl(spec, func)
    return wrapper

def hook_decorator(cb_type):
    """ Decorator to wrap hook definitions in. Registers hook. """
    def decorator_wrapper(*tags_or_func):
        if len(tags_or_func) == 1 and callable(tags_or_func[0]):
            # No tags were passed to this decorator
            func = tags_or_func[0]
            return HookImpl(cb_type, func)
        else:
            # We got some tags, so we need to produce the real decorator
            tags = tags_or_func
            def d(func):
                return HookImpl(cb_type, func, tags)
            return d
    return decorator_wrapper

Given = When = Then = And = step_decorator
Before = hook_decorator('before')
After = hook_decorator('after')
AfterStep = hook_decorator('after_step')

