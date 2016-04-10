# -*- coding: utf-8 -*-

import suspendable_unittest

class BaseSuspender(object):
    def __init__(self):
        self.add_actions()

    def add_actions(self):
        pass

    def add_action(self, method_name, method):
        suspendable_unittest.TestCase.add_action(method_name, method)

    def do_suspend(self, info):
        pass

    def after_suspend(self):
        pass

