# -*- coding: utf-8 -*-

try:
    import cPickle as pickle
except:
    import pickle
import zlib
import os
import os.path
import sys

from .testresult import TestResult
try:
    from _continuation import continulet
except:
    from .continulet import continulet
from .pauseforwarder import PauseForwarder

BASE_DIR = os.path.abspath(os.getcwd())
DEFAULT_STATEFILE_PATH = os.path.join(BASE_DIR, "teststate.bin")
PICKLE_PROTOCOL_VERSION = 1

def _run_test(con, param):
    test_suite = param[0]
    log_filename = param[1]
    loglevel = param[2]
    assertion_log = param[3]
    options = param[4] if param[4] is not None else {}

    sf = PauseForwarder(con)
    result = TestResult(filename=log_filename, loglevel=loglevel,
                        assertion_log=assertion_log, options=options)
    result.pause_forwarder = sf
    test_suite(result)
    if hasattr(result, "show_results"):
        result.show_results()
    result.close_logger()
    return ("finish", result)


class RestorableError(Exception):
    pass


class TestRunner(object):
    def __init__(self):
        self._continulet = None
        self._callback = {}

    def run(self, test_suite, pauser, filename=DEFAULT_STATEFILE_PATH,
            command_after_test=None, log_filename=None, loglevel=None,
            assertion_log=False, options=None):
        pauser.add_actions()

        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)

        ret_value = None
        exc = None
        first_run = False
        while True:
            if exc:
                if os.path.exists(filename):
                    # This means "failure of do_pause"
                    os.remove(filename)
                    pauser.after_pause()
            elif os.path.exists(filename):
                self.load_file(filename)
                pauser.after_pause()
            else:
                # New test
                continulet_args = (test_suite, log_filename, loglevel,
                                   assertion_log, options)
                self._continulet = continulet(_run_test, continulet_args)
                first_run = True
            action, info = self.run_continulet(ret_value, exc, pauser, first=first_run)
            ret_value = None
            exc = None
            first_run = False

            if action == "pause":
                try:
                    self.save_state(filename)
                except:
                    exc = sys.exc_info()[1]
                    continue

            try:
                if action == "pause":
                    ret_value = pauser.do_pause(info)
                elif action == "finish":
                    if hasattr(pauser, "do_finish"):
                        pauser.do_finish()
            except:
                exc = sys.exc_info()[1]
                sys.exc_clear()
            else:
                break

        if action == "finish" and callable(command_after_test):
            command_after_test({ "result": info })

    def load_file(self, filename):
        try:
            with open(filename, "rb") as f:
                pickled_data = zlib.decompress(f.read())
                self._continulet = pickle.loads(pickled_data)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def save_state(self, filename):
        if hasattr(self._continulet, "restorable"):
            if not self._continulet.restorable():
                raise RestorableError("current tasklet is not restorable")
        pickled_data = pickle.dumps(self._continulet, PICKLE_PROTOCOL_VERSION)
        with open(filename, "wb") as f:
            f.write(zlib.compress(pickled_data))

    def run_continulet(self, ret_value, exc, pauser, first=False):
        while True:
            if first:
                action, info = self._continulet.switch(None)
                first = False
            else:
                action, info = self._continulet.switch((ret_value, exc))
            exc = None
            ret_value = None

            if action in ("finish", "pause"):
                return (action, info)
            else:
                try:
                    ret_value = pauser.exec_callback(action, info)
                except:
                    exc = sys.exc_info()[1]
                    sys.exc_clear()
