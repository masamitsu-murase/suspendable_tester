# -*- coding: utf-8 -*-

import suspendable_runner

try:
    # for PyPy
    from _continuation import continulet
except ImportError:
    # for stackless python
    from continulet import continulet
import os
import pickle


class _RunnerInterface:
    def __init__(self, con):
        self.__con = con

    def suspend(self, info=None):
        self.__con.switch(("suspend", info))


def _run_test(con, test_func):
    runner = _RunnerInterface(con)
    result = suspendable_runner.SuspendableTestResult()
    result.runner = runner
    print("_run_test: %d" % id(runner))
    test_func(result)
    return ("finish", None)


# Runner is never pickled.
# _RunnerInterface is pickled instead.
class RunnerBase(object):
    def __init__(self):
        self._continulet = None
        self._callback = {}

    def load_continulet(self, test_func):
        pass

    def save_continulet(self):
        pass

    def exec_callback(self, action, info):
        if action in self._callback:
            for func in self._callback[action]:
                func(info)

    def add_callback(self, action, function):
        if action in self._callback:
            self._callback[action].append(function)
        else:
            self._callback[action] = [ function ]

    def run(self, test_func):
        self._continulet = self.load_continulet(test_func)
        while True:
            action, info = self._continulet.switch()
            if action == "finish":
                self.exec_callback(action, info)
                return (action, info)
            elif action == "suspend":
                self.save_continulet()
                self.exec_callback(action, info)
                return (action, info)
            self.exec_callback(action)


class Runner(RunnerBase):
    def __init__(self, pickle_filename):
        super(Runner, self).__init__()
        self._pickle_filename = pickle_filename

    def load_continulet(self, test_func):
        if os.path.exists(self._pickle_filename):
            try:
                with open(self._pickle_filename, "rb") as f:
                    return pickle.load(f)
            finally:
                os.remove(self._pickle_filename)
        else:
            return continulet(_run_test, test_func)

    def save_continulet(self):
        with open(self._pickle_filename, "wb") as f:
            pickle.dump(self._continulet, f)

if __name__ == "__main__":
    def hoge(r):
        a = 123
        print("hoge: 1")
        assert a == 123
        a += 1

        r.suspend()
        print("hoge: 2")
        assert a == 124
        a += 1

        r.suspend()
        print("hoge: 3")
        assert a == 125

    runner = Runner("M:/temp/hoge.bin")
    runner.run(hoge)

