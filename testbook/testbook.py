import sys
import importlib
import unittest
from functools import wraps

# Kudos to Michael Garod for the gist
# https://gist.github.com/mgarod/09aa9c3d8a52a980bd4d738e52e5b97a
def attach_test(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    
    return decorator


# !!! - Must be kept at bottom of module - !!!

# Involking double-underscore black magic
_modself_ = sys.modules[__name__]
testbook_attr = [a for a in _modself_.__dict__.keys() if not a.startswith('__')]
unittest_attr = [a for a in unittest.__all__ ]

for attrib in unittest_attr:
    if attrib in testbook_attr:
        continue

    _modself_.__setattr__(attrib, getattr(unittest, attrib))
    
# !!!
