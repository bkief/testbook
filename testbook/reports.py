
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
        for testcase in results:
            for test in results[testcase]:
                if results[testcase][test]['OUTCOME'] == 'SUCCESS':
                    successes += 1
                elif results[testcase][test]['OUTCOME'] == 'FAILURE':
                    failures += 1
                elif results[testcase][test]['OUTCOME'] == 'SKIPPED':
                    skips += 1
                elif results[testcase][test]['OUTCOME'] == 'ERROR':
                    errors += 1

                elapsed_time += results[testcase][test]['DURATION']

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