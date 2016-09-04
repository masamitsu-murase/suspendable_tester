# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser

import time
import re

class PickleTest(pausable_unittest.TestCase):
    def test_pickle(self):
        m = re.search(r"\s.", "ab cde")
        self.assertTrue(m)
        self.reboot()  # This will cause pickle error.
        self.assertTrue(m)

if __name__ == "__main__":
    pausable_unittest.main(testpauser.Pauser())

