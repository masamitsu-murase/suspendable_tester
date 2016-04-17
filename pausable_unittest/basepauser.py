# -*- coding: utf-8 -*-

import pausable_unittest

class BasePauser(object):
    def __init__(self):
        self.add_actions()

    def add_actions(self):
        pass

    def add_action(self, method_name, method):
        pausable_unittest.TestCase.add_action(method_name, method)

    def do_pause(self, info):
        pass

    def after_pause(self):
        pass

