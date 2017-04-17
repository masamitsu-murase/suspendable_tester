# -*- coding: utf-8 -*-

import unittest
import os
import os.path
import logging
import inspect
import functools
import contextlib


__pausable_unittest = True

def log_assertion1(method_name):
    u"""
    Wrapper method to log assertion.

    This wrapper expects that method takes 1 parameter and msg parameter.
    """
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
            if not error:
                frame = inspect.currentframe(1)
                self.log_for_assertion(method_name, frame.f_lineno,
                                       os.path.basename(frame.f_code.co_filename),
                                       msg)
    return wrapper


def log_assertion2(method_name):
    u"""
    Wrapper method to log assertion.

    This wrapper expects that method takes 1 parameter and msg parameter.
    """
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
            if not error:
                frame = inspect.currentframe(1)
                self.log_for_assertion(method_name, frame.f_lineno,
                                       os.path.basename(frame.f_code.co_filename),
                                       msg)
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
            if not error:
                frame = inspect.currentframe(1)
                self.log_for_assertion(method_name, frame.f_lineno,
                                       os.path.basename(frame.f_code.co_filename),
                                       msg)
    return wrapper


class TestCase(unittest.TestCase):
    def run(self, result):
        self.__result = result
        self.__pause_forwarder = result.pause_forwarder
        self.__logger = result.logger
        self.assertion_log = result.assertion_log
        self.options = result._options
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

    def log_for_assertion(self, method_name, lineno, filename, message):
        if self.assertion_log:
            text = "success %s (L%d in '%s')" % (method_name, lineno, filename)
            if message is not None:
                text += ": %s" % message
            self.logger.info(text)

    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        frame = inspect.currentframe(1)
        lineno = frame.f_lineno
        filename = frame.f_code.co_filename
        if (not callable(callableObj)) and (not args) and (not kwargs):
            @contextlib.contextmanager
            def helper():
                error = False
                msg = callableObj
                try:
                    with super(TestCase, self).assertRaises(excClass) as cm:
                        yield cm
                except:
                    error = True
                    raise
                finally:
                    if not error:
                        self.log_for_assertion("assertRaises", lineno,
                                               os.path.basename(filename),
                                               msg)
            return helper()
        else:
            error = False
            try:
                super(TestCase, self).assertRaises(excClass, callableObj, *args, **kwargs)
            except:
                error = True
                raise
            finally:
                if not error:
                    self.log_for_assertion("assertRaises", lineno,
                                           os.path.basename(filename),
                                           None)

    def assertRaisesRegexp(self, excClass, regexp, callableObj=None, *args, **kwargs):
        frame = inspect.currentframe(1)
        lineno = frame.f_lineno
        filename = frame.f_code.co_filename
        if (not callable(callableObj)) and (not args) and (not kwargs):
            @contextlib.contextmanager
            def helper():
                error = False
                msg = callableObj
                try:
                    with super(TestCase, self).assertRaisesRegexp(excClass, regexp) as cm:
                        yield cm
                except:
                    error = True
                    raise
                finally:
                    if not error:
                        self.log_for_assertion("assertRaisesRegexp", lineno,
                                               os.path.basename(filename),
                                               msg)
            return helper()
        else:
            error = False
            try:
                super(TestCase, self).assertRaisesRegexp(excClass, regexp, callableObj,
                                                         *args, **kwargs)
            except:
                error = True
                raise
            finally:
                if not error:
                    self.log_for_assertion("assertRaisesRegexp", lineno,
                                           os.path.basename(filename),
                                           None)

# 1 parameter
for name in ("assertTrue", "assertFalse", "assertIsNone", "assertIsNotNone"):
    setattr(TestCase, name, log_assertion1(name))

# 2 parameters
for name in ("assertEqual", "assertNotEqual", "assertIs", "assertIsNot",
             "assertIn", "assertNotIn", "assertIsInstance", "assertNotIsInstance",
             "assertGreater", "assertGreaterEqual", "assertLess", "assertLessEqual",
             ("assertRegexpMatches", "assertRegex"),
             ("assertNotRegexpMatches", "assertNotRegex"),
             "assertItemsEqual",
             "assertDictContainsSubset", "assertMultiLineEqual", "assertSequenceEqual",
             "assertListEqual", "assertTupleEqual", "assertSetEqual", "assertDictEqual"):
    if isinstance(name, tuple):
        if hasattr(unittest.TestCase, name[0]):
            setattr(TestCase, name[0], log_assertion2(name[0]))
        else:
            setattr(TestCase, name[1], log_assertion2(name[1]))
    else:
        setattr(TestCase, name, log_assertion2(name))

# assertAlmostEqual(first, second, places=7, msg=None, delta=None)
# assertNotAlmostEqual(first, second, places=7, msg=None, delta=None)
for name in ("assertAlmostEqual", "assertNotAlmostEqual"):
    setattr(TestCase, name, log_assertion_almost(name))
