# -*- coding: utf-8 -*-

import unittest

class TestCase(unittest.TestCase):
    def run(self, result):
        self.__result = result
        self.__pause_forwarder = result.pause_forwarder
        super(TestCase, self).run(result)

    def pause(self, info=None):
        self.__result.before_pause(info)
        self.__pause_forwarder.pause(info)
        self.__result.after_pause(info)

    @staticmethod
    def add_action(method_name, method):
        setattr(TestCase, method_name, method)
