# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import pausable_unittest.simplerunner as simplerunner
import testpauser
import pausable_unittest.dummypauser

def simple_test(pauser):
    pauser.assertTrue(True, "simple_test")
    pauser.reboot()
    pauser.assertTrue(True, "simple_test 2")


if __name__ == "__main__":
    simplerunner.main(simple_test, testpauser.Pauser())
