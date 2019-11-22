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


def main(title=None):
    testRunner = unittest.TextTestRunner(resultclass=runner.TestBookResult)
    r = unittest.main(verbosity=2, exit=False, argv=[''], 
                      testRunner=testRunner)
    sb.glue("testbook_result", r.result.json_result)
    if title:
        sb.glue("testbook_title", title)
    
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


def _discover(search_dir='.', recursive=False):
    logging.info("Search Dir: %s"%search_dir)
    logging.info("Recursive: %s"%recursive)
    search_dir = os.path.abspath(search_dir)
    tb_abspath = []
    for root, dirs, files in os.walk(search_dir):
        for f in files:
            if (fnmatch.fnmatch(f.lower(), "test*.ipynb") or
                  fnmatch.fnmatch(f.lower(), "*test.ipynb")):
                tb_abspath.append(os.path.join(root, f))

        if not recursive:
            break

    return tb_abspath


def run(search_dir='.', recursive=False):
    testset_start_time = dt.datetime.now()
    test_files = _discover(search_dir, recursive)
    logging.info("Discovered: %s"%test_files)
    test_results = {}

    if not os.path.exists(".\\reports"):
        os.makedirs('reports')

    proceeced_testbooks = []
    with JupyterEnv("venv_testbook") as jnb:
        for tf in test_files:
            out_notebook = os.path.join('reports', "_" + os.path.basename(tf))
            proceeced_testbooks.append(out_notebook)
            try:
                papermill.execute_notebook(tf, out_notebook, kernel_name=jnb.kernel)
            except Exception as e:
                print(e)

    for tf in proceeced_testbooks:
        tb = sb.read_notebook(tf)
        if 'testbook_title' in tb.scraps.data_dict:
            test_result_name = tb.scraps.data_dict['testbook_title']
        else:
            test_result_name = os.path.basename(tf)

        if 'testbook_result' in tb.scraps.data_dict:
            test_result = tb.scraps.data_dict['testbook_result']
        else:
            test_result = {}

        test_results[tf] = {'title': test_result_name,
                            'tests': test_result}

    logging.info("Generating report...")
    s = reports.generate_results_html(test_results, testset_start_time)

###############################################################################
#==============================================================================
###############################################################################

# !!! - Must be kept at bottom of module - !!!
# Involking double-underscore black magic
# _modself_ = sys.modules[__name__]
# testbook_attr = [a for a in _modself_.__dict__.keys() if not a.startswith('__')]
# unittest_attr = [a for a in unittest.__all__ ]

# for attrib in unittest_attr:
#     if attrib in testbook_attr:
#         continue

#     _modself_.__setattr__(attrib, getattr(unittest, attrib))

# !!!
