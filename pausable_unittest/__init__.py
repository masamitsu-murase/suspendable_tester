# coding: utf-8

from .testrunner import TestRunner
from .testcase import TestCase
from .basepauser import BasePauser

def main(pauser, filename="teststate.bin", command_after_test=None):
    import unittest
    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    TestRunner().run(suite, pauser, filename, command_after_test)

