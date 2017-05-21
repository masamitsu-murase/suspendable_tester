# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser

import time

class FailureTest(pausable_unittest.TestCase):
    def test_failure_exec_for_reboot(self):
        self.exec_for_reboot("invalid_command")

if __name__ == "__main__":
    pausable_unittest.main(testpauser.Pauser())
