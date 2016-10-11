# coding: utf-8

from .testrunner import TestRunner
from .testcase import TestCase
from .basepauser import BasePauser

def main(pauser, filename="teststate.bin", command_after_test=None, log_filename=None,
         loglevel=None):
    import unittest
    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    TestRunner().run(suite, pauser, filename=filename, command_after_test=command_after_test,
                     log_filename=log_filename, loglevel=loglevel)

