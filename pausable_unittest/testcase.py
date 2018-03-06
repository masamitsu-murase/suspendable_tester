# -*- coding: utf-8 -*-

import unittest
import os
import os.path
import logging
import inspect
import functools
import contextlib
try:
    import ctypes
except ImportError:
    ctypes = None
import sys

try:
    import stackless
    import stackless._wrap as stackless_wrap
except ImportError:
    stackless_wrap = None

__pausable_unittest = True

def safe_repr(obj, short=False):
    max_length = 40
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < max_length:
        return result
    return result[:max_length] + ' [truncated]...'

def _find_traceback_in_frame(frame):
    if stackless_wrap and hasattr(stackless_wrap, "frame"):
        # Really hacking code...
        # See prickelpit.c
        obj = stackless_wrap.frame.__reduce__(frame)
        try:
            for traceback in reversed(obj[-1][-1]):
                if inspect.istraceback(traceback):
                    return traceback
        except:
            pass
    return None

def _clear_locals_in_traceback(traceback, target_frames):
    try:
        frame = traceback.tb_frame
        if frame is None or frame in target_frames:
            return

        new_hash = {}
        for key in frame.f_locals:
            new_hash[key] = None
        if hasattr(ctypes, "pythonapi") and hasattr(ctypes.pythonapi, "PyFrame_LocalsToFast"):
            frame.f_locals.update(new_hash)
            ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))
        elif '__pypy__' in sys.builtin_module_names:
            import __pypy__
            if hasattr(__pypy__, "locals_to_fast"):
                frame.f_locals.update(new_hash)
                __pypy__.locals_to_fast(frame)
    finally:
        del frame

def _clear_unnecessary_locals():
    frame = inspect.currentframe().f_back
    target_frames = []
    try:
        while frame:
            locals_hash = frame.f_locals
            if locals_hash and "_tag_for_clear_unnecessary_locals" in locals_hash:
                break
            target_frames.append(frame)
            frame = frame.f_back
        traceback = sys.exc_info()[2]
        try:
            if traceback:
                while traceback:
                    _clear_locals_in_traceback(traceback, target_frames)
                    traceback = traceback.tb_next
            for frame in target_frames:
                traceback = _find_traceback_in_frame(frame)
                while traceback:
                    _clear_locals_in_traceback(traceback, target_frames)
                    traceback = traceback.tb_next
        finally:
            del traceback
    finally:
        del frame
        del target_frames


def log_assertion1(method_name):
    u"""
    Wrapper method to log assertion.

    This wrapper expects that method takes 1 parameter and msg parameter.
    """
    method = getattr(unittest.TestCase, method_name)

    @functools.wraps(method)
    def wrapper(self, arg, msg=None):
        error = False
        log_assertion_calling = self._log_assertion_calling
        if msg is None:
            msg = safe_repr(arg)
        else:
            msg = "%s (%s)" % (msg, safe_repr(arg))
        try:
            self._log_assertion_calling = True
            method(self, arg, msg)
        except:
            error = True
            raise
        finally:
            if not error and not log_assertion_calling:
                frame = inspect.currentframe().f_back
                self.log_for_assertion(method_name, frame.f_lineno,
                                       os.path.basename(frame.f_code.co_filename),
                                       msg)
            self._log_assertion_calling = log_assertion_calling
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
        log_assertion_calling = self._log_assertion_calling
        if msg is None:
            msg = "%s, %s" % (safe_repr(first), safe_repr(second))
        else:
            msg = "%s (%s, %s)" % (msg, safe_repr(first), safe_repr(second))
        try:
            self._log_assertion_calling = True
            method(self, first, second, msg)
        except:
            error = True
            raise
        finally:
            if not error and not log_assertion_calling:
                frame = inspect.currentframe().f_back
                self.log_for_assertion(method_name, frame.f_lineno,
                                       os.path.basename(frame.f_code.co_filename),
                                       msg)
            self._log_assertion_calling = log_assertion_calling
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
        log_assertion_calling = self._log_assertion_calling
        if msg is None:
            msg = "%s, %s" % (safe_repr(first), safe_repr(second))
        else:
            msg = "%s (%s, %s)" % (msg, safe_repr(first), safe_repr(second))
        try:
            self._log_assertion_calling = True
            return method(self, first, second, places, msg, delta)
        except:
            error = True
            raise
        finally:
            if not error and not log_assertion_calling:
                frame = inspect.currentframe().f_back
                self.log_for_assertion(method_name, frame.f_lineno,
                                       os.path.basename(frame.f_code.co_filename),
                                       msg)
            self._log_assertion_calling = log_assertion_calling
    return wrapper


class TestCase(unittest.TestCase):
    def run(self, result):
        _tag_for_clear_unnecessary_locals = None
        self.__result = result
        self.__pause_forwarder = result.pause_forwarder
        self.__logger = result.logger
        self.assertion_log = result.assertion_log
        self._log_assertion_calling = False
        self.options = result._options
        super(TestCase, self).run(result)

    def pause(self, info=None):
        self.__result.before_pause(info)
        status = self._extra_status()

        _clear_unnecessary_locals()

        try:
            self.__pause_forwarder.pause(info)
        finally:
            self._restore_extra_status(status)
        self.__result.after_pause(info)

    def call_pauser_callback(self, action, info=None):
        return self.__pause_forwarder.exec_callback(action, info)

    def _extra_status(self):
        status = {}
        status["cwd"] = os.path.abspath(os.getcwd())
        return status

    def _restore_extra_status(self, status):
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
        frame = inspect.currentframe().f_back
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
        frame = inspect.currentframe().f_back
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
             ("assertItemsEqual", None),
             ("assertDictContainsSubset", None),
             "assertMultiLineEqual", "assertSequenceEqual",
             "assertListEqual", "assertTupleEqual", "assertSetEqual", "assertDictEqual"):
    if isinstance(name, tuple):
        if hasattr(unittest.TestCase, name[0]):
            setattr(TestCase, name[0], log_assertion2(name[0]))
        elif name[1] is not None:
            setattr(TestCase, name[1], log_assertion2(name[1]))
    else:
        setattr(TestCase, name, log_assertion2(name))

# assertAlmostEqual(first, second, places=7, msg=None, delta=None)
# assertNotAlmostEqual(first, second, places=7, msg=None, delta=None)
for name in ("assertAlmostEqual", "assertNotAlmostEqual"):
    setattr(TestCase, name, log_assertion_almost(name))
