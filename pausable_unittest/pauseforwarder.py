# -*- coding: utf-8 -*-

class PauseForwarder(object):
    def __init__(self, con):
        self.__con = con

    def pause(self, info=None):
        exc = self.__con.switch(("pause", info))
        if exc:
            raise exc

