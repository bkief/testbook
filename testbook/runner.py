from unittest import TextTestResult
import traceback
import time

from . import reports

class _TestInfo(object):
    """" Keeps information about the execution of a test method. """

    (SUCCESS, FAILURE, ERROR, SKIP) = range(4)

    def __init__(self, test_result, test_method, outcome=SUCCESS,
                 err=None, subTest=None):
        self.test_result = test_result
        self.outcome = outcome
        self.elapsed_time = 0
        self.err = err
        self.stdout = test_result._stdout_data
        self.stderr = test_result._stderr_data

        self.is_subtest = subTest is not None

        self.test_description = self.test_result.getDescription(test_method)
        self.test_exception_info = (
            '' if outcome in (self.SUCCESS, self.SKIP)
            else self.test_result._exc_info_to_string(
                self.err, test_method))

        self.test_name = testcase_name(test_method)
        if not self.is_subtest:
            self.test_id = test_method.id()
        else:
            self.test_id = subTest.id()

    def id(self):
        return self.test_id

    def test_finished(self):
        self.elapsed_time = self.test_result.stop_time - self.test_result.start_time

    def get_description(self):
        return self.test_description

    def get_error_info(self):
        return self.test_exception_info


class _SubTestInfos(object):
    # TODO: make better: inherit _TestInfo?
    (SUCCESS, FAILURE, ERROR, SKIP) = range(4)

    def __init__(self, test_id, subtests):
        self.subtests = subtests
        self.test_id = test_id
        self.outcome = self.check_outcome()

    def check_outcome(self):
        outcome = _TestInfo.SUCCESS
        for subtest in self.subtests:
            if subtest.outcome != _TestInfo.SUCCESS:
                outcome = _TestInfo.FAILURE
                break
        return outcome

###

class TestBookResult(TextTestResult):

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.json_result = {}
        self.testcasename = ''
        self.testmethodname = ''
        self.start_time = 0

    def startTestRun(self):
        super().startTestRun()

    def startTest(self, test):
        self.testcasename = test.__class__.__name__
        self.testmethodname = test._testMethodName
        if self.testcasename not in self.json_result:
            self.json_result[self.testcasename] = {}
        if self.testmethodname not in self.json_result[self.testcasename]:
            self.json_result[self.testcasename][self.testmethodname] = {}
        self.start_time = time.time()

        super().startTest(test)

    def stopTest(self, test):
        elapsed_time = time.time() - self.start_time
        result_summary = {'duration': elapsed_time,
                          'duration_fmt': reports._format_duration(elapsed_time), 
                          'description': self.getDescription(test),
                          'test_id': '1.1'
                          }
        self.json_result[self.testcasename][self.testmethodname].update(result_summary)
        super().stopTest(test)

    def addSuccess(self, test):
        result_summary = {'outcome': 'SUCCESS',
                          'exception': ''
                          }
        self.json_result[self.testcasename][self.testmethodname].update(result_summary)
        super().addSuccess(test)

    def addError(self, test, err):
        result_summary = {'outcome': 'ERROR',
                          'exception': self._exc_info_to_string(err, test)
                          }
        self.json_result[self.testcasename][self.testmethodname].update(result_summary)
        super().addError(test, err)

    def addFailure(self, test, err):
        result_summary = {'outcome': 'FAILURE',
                          'exception': self._exc_info_to_string(err, test)
                          }
        self.json_result[self.testcasename][self.testmethodname].update(result_summary)
        super().addFailure(test, err)

    def addSkip(self, test, reason):
        result_summary = {'outcome': 'SKIPPED',
                          'exception': ''
                          }
        self.json_result[self.testcasename][self.testmethodname].update(result_summary)
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        result_summary = {'outcome': 'EXPECTEDFAILURE'}
        self.json_result[self.testcasename][self.testmethodname].update(result_summary)
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        result_summary = {'outcome': 'UNEXPECTEDSUCCESS'}
        self.json_result[self.testcasename][self.testmethodname].update(result_summary)
        super().addUnexpectedSuccess(test)


    # def printErrors(self):
    #     if self.dots or self.showAll:
    #         self.stream.writeln()
    #     self.printErrorList('ERROR', self.errors)
    #     self.printErrorList('FAIL', self.failures)

    # def printErrorList(self, flavour, errors):
    #     for test, err in errors:
    #         self.stream.writeln(self.separator1)
    #         self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
    #         self.stream.writeln(self.separator2)
    #         self.stream.writeln("%s" % err)

