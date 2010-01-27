#-*- coding: utf8 -*-
import imp
import logging
import re
import sys
import traceback

__all__ = ['Given', 'When', 'Then', 'And', 'Before', 'After', 'AfterStep']

log = logging.getLogger('nose.plugins.freshen')

class AmbiguousStepImpl(Exception):
    
    def __init__(self, match, impl1, impl2):
        self.match = match
        self.impl1 = impl1
        self.impl2 = impl2
        super(AmbiguousStepImpl, self).__init__('Ambiguous: "%s"\n %s, %s' % (match, impl1, impl2))

class UndefinedStepImpl(Exception):
    
    def __init__(self, match):
        self.match = match
        super(UndefinedStepImpl, self).__init__('Undefined step: "%s"' % match)

class StepImpl(object):
    
    def __init__(self, spec, func):
        self.spec = spec
        self.func = func
        self.re_spec = re.compile(spec)
    
    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)
    
    def match(self, match):
        return self.re_spec.match(match)

class HookImpl(object):
    
    def __init__(self, cb_type, func, tags=[]):
        self.cb_type = cb_type
        self.tags = tags
        self.func = func
        self.tags = tags
    
    def __call__(self, scenario):
        self.func(scenario)


class StepImplRegistry(object):
    
    def __init__(self, tag_matcher_class):
        self.steps = []
        self.hooks = {
            'before': [],
            'after': [],
            'after_step': []
        }
        self.tag_matcher_class = tag_matcher_class
        self.paths = []
    
    def load_steps_impl(self, path):
        """
        Load the step implementations from a python module, named 'steps', found at the given path.
        """
        if path not in self.paths:
            log.debug("Looking for step defs in %s" % path)
            try:
                info = imp.find_module("steps", [path])
                mod = imp.load_module("steps", *info)
                self.paths.append(path)
            except ImportError, e:
                log.debug(traceback.format_exc())
                return
            
            for item_name in dir(mod):
                item = getattr(mod, item_name)
                if isinstance(item, StepImpl):
                    self.steps.append(item)
                elif isinstance(item, HookImpl):
                    self.hooks[item.cb_type].append(item)
    
    def find_step_impl(self, match):
        """
        Find the implementation of the step for the given match string. Returns the StepImpl object
        corresponding to the implementation, and the arguments to the step implementation. If no
        implementation is found, raises UndefinedStepImpl. If more than one implementation is
        found, raises AmbiguousStepImpl.
        """
        result = None
        for si in self.steps:
            matches = si.match(match)
            if matches:
                if result:
                    raise AmbiguousStepImpl(match, result[0], si)
                result = si, matches.groups()
        
        if not result:
            raise UndefinedStepImpl(match)
        return result
    
    def get_hooks(self, cb_type, tags=[]):
        return [h for h in self.hooks[cb_type] if self.tag_matcher_class(tags).check_match(h.tags)]


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

