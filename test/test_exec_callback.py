# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser

import time
import re

class ExecCallbackTest(pausable_unittest.TestCase):
    def test_exec_callback(self):
        self.assertEqual(self.bat_path("base"), "base_sample", "bat_path should return XXX_sample")
        try:
            self.create_bat()
        except:
            self.assertFalse("create_bat should not raise any errors.")

if __name__ == "__main__":
    pauser = testpauser.Pauser()
    pausable_unittest.main(pauser)
