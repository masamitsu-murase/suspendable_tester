# -*- coding: utf-8 -*-

import pickle
import zlib
import os

from .testresult import TestResult
from .continulet import continulet


class _RunnerInterface(object):
    def __init__(self, con):
        self.__con = con

    def suspend(self, info=None):
        self.__con.switch(("suspend", info))


def _run_test(con, test_suite):
    ri = _RunnerInterface(con)
    result = TestResult()
    result.suspendable_testrunner = ri
    test_suite(result)
    return ("finish", None)


class TestRunner(object):
    def __init__(self):
        self._continulet = None
        self._callback = {}

    def run(self, test_suite, suspender, filename="teststate.bin"):
        if os.path.exists(filename):
            self.load_file(filename)
        else:
            self._continulet = continulet(_run_test, test_suite)
        action, info = self.run_continulet()
        if action == "suspend":
            self.save_state(filename)
            suspender.do_suspend(info)
        elif action == "finish":
            if hasattr(suspender, "do_finish"):
                suspender.do_finish()

    def load_file(self, filename):
        try:
            with open(filename, "rb") as f:
                pickled_data = zlib.decompress(f.read())
                self._continulet = pickle.loads(pickled_data)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def save_state(self, filename):
        with open(filename, "wb") as f:
            pickled_data = pickle.dumps(self._continulet)
            f.write(zlib.compress(pickled_data))

    def exec_callback(self, action, info):
        if action in self._callback:
            for func in self._callback[action]:
                func(info)

    def add_callback(self, action, function):
        if action in self._callback:
            self._callback[action].append(function)
        else:
            self._callback[action] = [ function ]

    def run_continulet(self):
        while True:
            action, info = self._continulet.switch()
            self.exec_callback(action, info)
            if action in ("finish", "suspend"):
                return (action, info)

