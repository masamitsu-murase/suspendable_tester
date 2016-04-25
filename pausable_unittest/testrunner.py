# -*- coding: utf-8 -*-

import pickle
import zlib
import os
import os.path
import sys

from .testresult import TestResult
from .continulet import continulet
from .pauseforwarder import PauseForwarder

BASE_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
DEFAULT_STATEFILE_PATH = os.path.join(BASE_DIR, "teststate.bin")

def _run_test(con, test_suite):
    sf = PauseForwarder(con)
    result = TestResult()
    result.pause_forwarder = sf
    test_suite(result)
    if hasattr(result, "show_results"):
        result.show_results()
    return ("finish", None)


class TestRunner(object):
    def __init__(self):
        self._continulet = None
        self._callback = {}

    def run(self, test_suite, pauser, filename=DEFAULT_STATEFILE_PATH):
        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)

        exc = None
        while True:
            if os.path.exists(filename):
                self.load_file(filename)
                pauser.after_pause()
            else:
                self._continulet = continulet(_run_test, test_suite)
            action, info = self.run_continulet(exc)
            try:
                if action == "pause":
                    self.save_state(filename)
                    pauser.do_pause(info)
                elif action == "finish":
                    if hasattr(pauser, "do_finish"):
                        pauser.do_finish()
            except:
                exc = sys.exc_info()[1]
            else:
                break

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

    def run_continulet(self, exc):
        while True:
            action, info = self._continulet.switch(exc)
            exc = None
            self.exec_callback(action, info)
            if action in ("finish", "pause"):
                return (action, info)

