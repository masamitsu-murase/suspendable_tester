# -*- coding: utf-8 -*-

import unittest
import os
import logging


__pausable_unittest = True

def log_assertion1(method_name):
    u"""
    Wrapper method to log assertion.

    This wrapper expects that method takes 1 parameter and msg parameter.
    """
    import functools
    method = getattr(unittest.TestCase, method_name)

    @functools.wraps(method)
    def wrapper(self, arg, msg=None):
        error = False
        try:
            method(self, arg, msg)
        except:
            error = True
            raise
        finally:
            if not error and self.assertion_log:
                self.logger.info("success %s: %s", method_name, msg)
    return wrapper


def log_assertion2(method_name):
    u"""
    Wrapper method to log assertion.

    This wrapper expects that method takes 1 parameter and msg parameter.
    """
    import functools
    method = getattr(unittest.TestCase, method_name)

    @functools.wraps(method)
    def wrapper(self, first, second, msg=None):
        error = False
        try:
            method(self, first, second, msg)
        except:
            error = True
            raise
        finally:
            if not error and self.assertion_log:
                self.logger.info("success %s: %s", method_name, msg)
    return wrapper


def log_assertion_almost(method_name):
    u"""
    Wrap assertAlmostEqual and assertNotAlmostEqual.
    """
    import functools
    method = getattr(unittest.TestCase, method_name)

    @functools.wraps(method)
    def wrapper(self, first, second, places=7, msg=None, delta=None):
        error = False
        try:
            return method(self, first, second, places, msg, delta)
        except:
            error = True
            raise
        finally:
            if not error and self.assertion_log:
                self.logger.info("success %s: %s", method_name, msg)
    return wrapper


class TestCase(unittest.TestCase):
    def run(self, result):
        self.__result = result
        self.__pause_forwarder = result.pause_forwarder
        self.__logger = result.logger
        self.assertion_log = result.assertion_log
        super(TestCase, self).run(result)

    def pause(self, info=None):
        self.__result.before_pause(info)
        status = self.extra_status()

        self.__pause_forwarder.pause(info)

        self.restore_extra_status(status)
        self.__result.after_pause(info)

    def extra_status(self):
        status = {}
        status["cwd"] = os.path.abspath(os.getcwd())
        return status

    def restore_extra_status(self, status):
        try:
            os.chdir(status["cwd"])
        except:
            self.logger.error("Cannot change directory to '%s'.", status["cwd"])

    @property
    def logger(self):
        return self.__logger

    @staticmethod
    def add_action(method_name, method):
        setattr(TestCase, method_name, method)


# 1 parameter
for name in ("assertTrue", "assertFalse", "assertIsNone", "assertIsNotNone"):
    setattr(TestCase, name, log_assertion1(name))

# 2 parameters
for name in ("assertEqual", "assertNotEqual", "assertIs", "assertIsNot",
             "assertIn", "assertNotIn", "assertIsInstance", "assertNotIsInstance",
             "assertGreater", "assertGreaterEqual", "assertLess", "assertLessEqual",
             "assertRegexpMatches", "assertNotRegexpMatches", "assertItemsEqual",
             "assertDictContainsSubset", "assertMultiLineEqual", "assertSequenceEqual",
             "assertListEqual", "assertTupleEqual", "assertSetEqual", "assertDictEqual"):
    setattr(TestCase, name, log_assertion2(name))

# assertAlmostEqual(first, second, places=7, msg=None, delta=None)
# assertNotAlmostEqual(first, second, places=7, msg=None, delta=None)
for name in ("assertAlmostEqual", "assertNotAlmostEqual"):
    setattr(TestCase, name, log_assertion_almost(name))

# assertRaises(exc, fun, *args, **kwds)
# assertRaisesRegexp(exc, r, fun, *args, **kwds)

