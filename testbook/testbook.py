import sys
import os
import importlib
import unittest
import time
import json
import glob
from functools import wraps
import datetime as dt

import scrapbook.api as sb
import papermill

from . import runner
from . import reports

def attach_test(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    
    return decorator

def main():
    testRunner = unittest.TextTestRunner(resultclass=runner.TestBookResult)
    r = unittest.main(verbosity=2, exit=False, argv=[''], 
                           testRunner=testRunner)
    
    sb.glue("testbook_result", r.result.json_result)
    with open('test_result.json', 'w') as w:
        json.dump(r.result.json_result, w)

    return r

def discover(search_dir='.', recurcive=True):
    for f in os.walk(search_dir):
        pass
    return ['tests/simple_test.ipynb']

def _get_testbook_title(tf):
    return 'Test File 1'

def run():
    testset_start_time = dt.datetime.now()
    test_files = discover()
    test_results = {}
    import json
    import pprint
    for tf in test_files:
        papermill.execute_notebook(tf, tf)
        os.system("py -3 %s"%tf)
        test_result_name = _get_testbook_title(tf)
        # with open('test_result.json') as f:
        #     test_result = json.load(f)

        tb = sb.read_notebook(tf)
        test_result = tb.scraps.data_dict['testbook_result']
        
        pprint.pprint(test_result)
        
        test_results[tf] = {'title': test_result_name,
                            'tests': test_result}
    
    s = reports.generate_results_html(test_results, testset_start_time)
    #print(s)

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
