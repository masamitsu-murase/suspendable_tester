
import sys

class SuspendableTestRunner(object):
    def __init__(self):
        pass

    def run(self, test):
        result = SuspendableTestResult()
        test(result)


class SuspendableTestResult(object):
    def __init__(self, stream_type="stdout", filename=None):
        self._stream_type = stream_type
        self._results = []
        self._file = None
        self.filename = filename

    def _filterResult(self, type):
        return [ x for x[0] == type in self._results ]

    def errors(self):
        return self._filterResult("error")

    def failures(self):
        return self._filterResult("failure")

    def successes(self):
        return self._filterResult("success")

    def expected_failures(self):
        return self._filterResult("expected_failure")

    def skips(self):
        return self._filterResult("skip")

    def unexpected_successes(self):
        return self._filterResult("unexpected_successes")

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
        if self.descriptions and doc_first_line:
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

    def _writeln(str):
        output = self._output_stream()
        output.writeln(str)

    def startTest(self, test):
        self._write(self.getDescription(test))
        self._write(" ... ")

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

