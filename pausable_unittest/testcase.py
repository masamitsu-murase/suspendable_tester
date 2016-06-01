# -*- coding: utf-8 -*-

import unittest
import os

class TestCase(unittest.TestCase):
    def run(self, result):
        self.__result = result
        self.__pause_forwarder = result.pause_forwarder
        self.__logger = result.logger
        super(TestCase, self).run(result)

    def pause(self, info=None):
        self.__result.before_pause(info)
        status = self.extra_status()

        self.__pause_forwarder.pause(info)

        self.restore_extra_status(status)
        self.__result.after_pause(info)

    def extra_status(self):
        status = {}
        status["cwd"] = os.path.abspath(os.getcwd())
        return status

    def restore_extra_status(self, status):
        try:
            os.chdir(status["cwd"])
        except:
            self.logger.error("Cannot change directory to '%s'.", status["cwd"])

    @property
    def logger(self):
        return self.__logger

    @staticmethod
    def add_action(method_name, method):
        setattr(TestCase, method_name, method)
