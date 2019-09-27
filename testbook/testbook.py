import sys
import importlib
import unittest
import time
from functools import wraps

import scrapbook

import runner

def attach_test(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    
    return decorator

def main():
    testRunner = unittest.TextTestRunner(resultclass=runner.TestBookResult)
    result = unittest.main(verbosity=2, exit=False, argv=[''], 
                           testRunner=testRunner)

    return result

    
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
