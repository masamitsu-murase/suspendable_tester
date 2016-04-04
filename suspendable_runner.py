
import sys
import traceback

class SuspendableTestRunner(object):
    def __init__(self):
        pass

    def run(self, test):
        result = SuspendableTestResult()
        test(result)


class SuspendableTestResult(object):
    def __init__(self, stream_type="stdout", filename=None):
        self.shouldStop = False
        self.failFast = False

        self._stream_type = stream_type
        self._results = []
        self._file = None
        self.filename = filename

    def _filterResult(self, type):
        return [ (x[1], x[2]) for x in self._results if x[0] == type ]

    @property
    def errors(self):
        return self._filterResult("error")

    @property
    def failures(self):
        return self._filterResult("failure")

    @property
    def skipped(self):
        return self._filterResult("skip")

    @property
    def expectedFailures(self):
        return self._filterResult("expected_failure")

    @property
    def unexpectedSuccesses(self):
        return self._filterResult("unexpected_successes")

    @property
    def successes(self):
        return self._filterResult("success")

    @property
    def testsRun(self):
        return len(self._results)

    def stop(self):
        self.shouldStop = True


    def _outputResult(self):
        pass

    def __getstate__():
        return { "_stream_type": self._stream_type,
                 "_result": self._results,
                 "filename": self.filename }

    def addResult(self, type, test, err=None):
        self._results.append((type, test, err))

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def _output_stream(self):
        if self._stream_type == "stdout":
            return sys.stdout
        elif self._stream_type == "stderr":
            return sys.stderr
        else:
            raise "Invalid _stream_type"

    def _write(self, str):
        output = self._output_stream()
        output.write(str)

    def _writeln(self, str):
        output = self._output_stream()
        output.write(str + "\n")

    def startTest(self, test):
        self._write(self.getDescription(test))
        self._write(" ... ")

    def stopTest(self, test):
        pass

    def startTestRun(self, test):
        pass

    def stopTestRun(self, test):
        pass

    def addSuccess(self, test):
        self.addResult("success", test)
        self._writeln("ok")

    def addError(self, test, err):
        self.addResult("error", test, err)
        self._writeln("ERROR")

    def addFailure(self, test, err):
        self.addResult("failure", test, err)
        self._writeln("FAIL")

    def addSkip(self, test, reason):
        self.addResult("skip", test, reason)
        self._writeln("skipped {0!r}".format(reason))

    def addExpectedFailure(self, test, err):
        self.addResult("expected_failure", test, err)
        self._writeln("expected failure")

    def addUnexpectedSuccess(self, test):
        self.addResult("unexpected_success", test)
        self._writeln("unexpected success")

    def _is_relevant_tb_level(self, tb):
        # return '__unittest' in tb.tb_frame.f_globals
        return False

    def _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
        else:
            length = None
        tb_e = traceback.TracebackException(
            exctype, value, tb, limit=length, capture_locals=self.tb_locals)
        msgLines = list(tb_e.format())

        return ''.join(msgLines)

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

