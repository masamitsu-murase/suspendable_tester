# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import pausable_unittest.windowspauser as windowspauser
import unittest

import time
import re


class WindowsPauserTest(unittest.TestCase):
    def setUp(self):
        self.pauser = windowspauser.Pauser()

    def test_is_admin(self):
        self.assertTrue(self.pauser.is_admin())


if __name__ == "__main__":
    unittest.main()
