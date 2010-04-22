#-*- coding: utf8 -*-

from nose.tools import *
import re as _re
import difflib as _difflib

__unittest = 1

def assert_looks_like(first, second, msg=None):
    """ Compare two strings if all contiguous whitespace is coalesced. """
    first = _re.sub("\s+", " ", first.strip())
    second = _re.sub("\s+", " ", second.strip())
    if first != second:
        raise AssertionError(msg or "%r does not look like %r" % (first, second))

_assert_equal = assert_equal
def assert_equal(first, second, msg=None):
    doit = all(isinstance(s, basestring) for s in [first, second]) and \
           any("\n" in s for s in [first, second])
    
    if not doit:
        return _assert_equal(first, second, msg)
        
    if first != second:
        diff = _difflib.unified_diff(first.split("\n"), second.split("\n"),
                                     "expected", "actual", lineterm="")
        diff = "    " + "\n    ".join(diff)
        raise AssertionError(msg or "Strings not equal\n" + diff)

assert_equals = assert_equal

