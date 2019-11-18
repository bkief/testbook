
import os
import json

from jinja2 import Template


DEFAULT_TEMPLATE = os.path.join(os.path.dirname(__file__), "template", "report_template.html")

def render_html(template, **kwargs):
    with open(DEFAULT_TEMPLATE, 'r') as t:
        template_file = t.read()
    template = Template(template_file)
    return template.render(**kwargs)

def _format_duration(elapsed_time):
        """Format the elapsed time in seconds, or milliseconds if the duration is less than 1 second."""
        if elapsed_time > 1:
            duration = '{:2.2f} s'.format(elapsed_time)
        else:
            duration = '{:d} ms'.format(int(elapsed_time * 1000))
        return duration


def get_results_summary(results, testset_start_time):
        """Create a summary of the outcomes of all given test results."""

        elapsed_time = 0
        failures = errors = skips = successes = 0
        for testset_name, testset in results.items():
            _elapsed_time = 0
            _failures = _errors = _skips = _successes = 0
            for testcase_name, testcase in testset['tests'].items():
                for test_name, test in testcase.items():
                    if test['outcome'] == 'SUCCESS':
                        _successes += 1
                    elif test['outcome'] == 'FAILURE':
                        _failures += 1
                    elif test['outcome'] == 'SKIPPED':
                        _skips += 1
                    elif test['outcome'] == 'ERROR':
                        _errors += 1

                    _elapsed_time += test['duration']

            successes += _successes
            failures += _failures
            skips += _skips
            errors += _errors
            elapsed_time += _elapsed_time

            if _elapsed_time > 1:
                duration = '{:2.2f} s'.format(_elapsed_time)
            else:
                duration = '{:d} ms'.format(int(_elapsed_time * 1000))

            results[testset_name]['summary'] = {'total': sum([_successes,
                                                              _failures,
                                                              _skips,
                                                              _errors]),
                                                 'success': _successes,
                                                 'falure': _failures,
                                                 'skip': _skips,
                                                 'error': _errors,
                                                 'duration': duration
                                                }
            

        results_summary = {
            "total": failures+errors+skips+successes,
            "error": errors,
            "failure": failures,
            "skip": skips,
            "success": successes,
            "duration": _format_duration(elapsed_time),
            "testSetStartTime": testset_start_time
        }

        return results_summary

def generate_results_html(results, testset_start_time):
    status_tags = {'SUCCESS': 'success', 'FAILURE':'danger', 'ERROR':'warning', 'SKIPPED':'info'}
    results_summary = get_results_summary(results, testset_start_time)

    html_file = render_html(DEFAULT_TEMPLATE, 
                            title="Test Results", 
                            summary = results_summary,
                            all_results = results,
                            status_tags=status_tags)
    
    if not os.path.exists(".\\reports"):
        os.makedirs('reports')

    with open('.\\reports\\test_results.html', 'w') as w:
        w.write(html_file)