# -*- coding: utf-8 -*-

class PauseForwarder(object):
    def __init__(self, con):
        self.__con = con

    def pause(self, info=None):
        return self.exec_callback("pause", info)

    def exec_callback(self, action, info=None):
        ret_value, exc = self.__con.switch((action, info))
        if exc:
            raise exc
        return ret_value

