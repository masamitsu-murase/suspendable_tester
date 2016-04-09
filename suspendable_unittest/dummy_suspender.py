
import unittest

class Suspender(object):
    def __init__(self):
        self.add_actions()

    def add_actions(self):
        def shutdown(self, wake_after_sec=None):
            self.suspend(("shutdown", wake_after_sec))
        unittest.TestCase.shutdown = shutdown

    def do_suspend(self, info):
        if info[0] == "shutdown":
            if info[1] is not None:
                pass
            print("Shutdown")
            print("Run again")


