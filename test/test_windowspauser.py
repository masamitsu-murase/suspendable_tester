# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import pausable_unittest.windowspauser as windowspauser
import unittest
import subprocess
import time
import re


class WindowsPauserTest(unittest.TestCase):
    def setUp(self):
        self.pauser = windowspauser.Pauser()

    def test_is_admin(self):
        self.assertTrue(self.pauser.is_admin())

    def test_register_startup(self):
        if not self.pauser.is_admin():
            return

        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_output(["schtasks", "/Query", "/TN", windowspauser.TASK_NAME], stderr=subprocess.STDOUT)
        self.pauser.register_startup()
        output = subprocess.check_output(["schtasks", "/Query", "/TN", windowspauser.TASK_NAME])
        self.assertTrue(output)

        self.pauser.unregister_startup()
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_output(["schtasks", "/Query", "/TN", windowspauser.TASK_NAME], stderr=subprocess.STDOUT)


if __name__ == "__main__":
    unittest.main()
