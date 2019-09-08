# -*- coding: utf-8 -*-

from .testrunner import TestRunner
from .testcase import TestCase


class TestCase(TestCase):
    def __init__(self, func):
        self.__func = func
        super(TestCase, self).__init__()

    def runTest(self):
        self.__func(self)


def main(func,
         pauser,
         filename="teststate.bin",
         command_after_test=None,
         log_filename=None,
         loglevel=None):
    TestRunner().run(TestCase(func),
                     pauser,
                     filename=filename,
                     command_after_test=command_after_test,
                     log_filename=log_filename,
                     loglevel=loglevel)
