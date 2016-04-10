# -*- coding: utf-8 -*-

import unittest

class TestCase(unittest.TestCase):
    def run(self, result):
        self.__result = result
        self.__suspend_forwarder = result.suspend_forwarder
        super(TestCase, self).run(result)

    def suspend(self, info=None):
        self.__result.before_suspend(info)
        self.__suspend_forwarder.suspend(info)
        self.__result.after_suspend(info)

