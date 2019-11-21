import sys
import os
import unittest
import fnmatch
import datetime as dt
import logging

import scrapbook.api as sb
import papermill
import ipykernel.kernelspec as ipyk
import jupyter_client.kernelspec as jupyter_kernel

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

    return r


###############################################################################
#==============================================================================
###############################################################################

class JupyterEnv:
    def __init__(self, kernel_name):
        self.pyinterpreter = sys.executable
        self.kernel = kernel_name

    def __enter__(self):
        ipyk.install(user=True, kernel_name=self.kernel, 
                     display_name=self.kernel)
        return self 

    def __exit__(self, type, value, traceback):
        jupyter_kernel.KernelSpecManager().remove_kernel_spec(self.kernel)


def discover(search_dir='.', recurcive=True):
    search_dir = os.path.abspath(search_dir)
    tb_abspath = []
    for root, dirs, files in os.walk(search_dir):
        for f in files:
            if (fnmatch.fnmatch(f.lower(), "test*.ipynb") or
                  fnmatch.fnmatch(f.lower(), "*test.ipynb")):
                tb_abspath.append(os.path.join(root, f))

        if not recurcive:
            break

    return tb_abspath

def _get_testbook_title(tf):
    return 'Test File 1'


def run(search_dir='.', recurcive=True):
    testset_start_time = dt.datetime.now()
    test_files = discover(search_dir, recurcive)
    print(test_files)
    test_results = {}
    import pprint
    with JupyterEnv("venv_testbook") as jnb:
        for tf in test_files:

            papermill.execute_notebook(tf, tf, kernel_name=jnb.kernel)

    for tf in test_files:
        test_result_name = _get_testbook_title(tf)

        tb = sb.read_notebook(tf)
        if 'testbook_result' in tb.scraps.data_dict:
            test_result = tb.scraps.data_dict['testbook_result']
        else:
            test_result = {}
        
        pprint.pprint(test_result)
        
        test_results[tf] = {'title': test_result_name,
                            'tests': test_result}
    
    s = reports.generate_results_html(test_results, testset_start_time)

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
