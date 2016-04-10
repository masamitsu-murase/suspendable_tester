# -*- coding: utf-8 -*-

class SuspendForwarder(object):
    def __init__(self, con):
        self.__con = con

    def suspend(self, info=None):
        self.__con.switch(("suspend", info))

