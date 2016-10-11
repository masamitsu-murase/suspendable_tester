# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser
import pausable_unittest.dummypauser

import time
import re

class PauserTest(pausable_unittest.TestCase):
    def test_pauser(self):
        self.assertFalse(hasattr(self, "exec_for_reboot"), "method for testpauser should not copied to TestCase")

if __name__ == "__main__":
    dummy = pausable_unittest.dummypauser.Pauser()
    test = testpauser.Pauser()
    pausable_unittest.main(dummy)

