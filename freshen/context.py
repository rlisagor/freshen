#-*- coding: utf8 -*-

__all__ = ['glc', 'ftc', 'scc']

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

