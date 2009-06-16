__all__ = ['Given', 'When', 'Then', 'load_feature']

import imp
import os
import re
import parser
import traceback

spec_registry = {}

def step(spec):
    def wrapper(func):
        r = re.compile(spec)
        spec_registry[r] = func
        return func
    return wrapper

Given = step
When = step
Then = step

def find_match(s):
    result = None
    for r, f in spec_registry.iteritems():
        matches = r.match(s)
        if matches:
            if result:
                raise Exception("Ambiguous: %s" % s)
            result = f
    
    return f(*matches.groups())

def load_feature(fname):
    fname = os.path.abspath(fname)
    path = os.path.dirname(fname)
    
    info = imp.find_module("steps", [path])
    mod = imp.load_module("steps", *info)
    
    #return parser.parse_file(fname)

