# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import pausable_unittest.dummypauser
import unittest

import time
import re


class SubtestTest(pausable_unittest.TestCase):
    @unittest.skipUnless(hasattr(unittest.TestCase, "subTest"), "for Python3")
    def test_subtest(self):
        for i in range(2):
            with self.subTest("check1", i=i):
                self.reboot()
                self.assertEqual(i, 0)
            self.assertTrue(True)

        for i in range(2):
            with self.subTest("check2", i=i):
                try:
                    self.assertEqual(i, 0)
                finally:
                    self.reboot()

    @unittest.skipUnless(hasattr(unittest.TestCase, "subTest"), "for Python3")
    def test_exception(self):
        for i in range(2):
            with self.subTest("check3", i=i):
                raise RuntimeError()

        with self.subTest("check4"):
            try:
                self.assertTrue(False)
            finally:
                raise RuntimeError()


if __name__ == "__main__":
    dummy = pausable_unittest.dummypauser.Pauser()
    pausable_unittest.main(dummy, assertion_log=True)
