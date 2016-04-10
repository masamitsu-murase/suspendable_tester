# coding: utf-8

from .testrunner import TestRunner
from .testcase import TestCase

def main(suspender, filename="teststate.bin"):
    import unittest
    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    TestRunner().run(suite, suspender, filename)

