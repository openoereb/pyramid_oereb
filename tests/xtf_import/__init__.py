# -*- coding: utf-8 -*-


class MockSession(object):
    def __init__(self):
        self._data = []

    def add(self, item):
        self._data.append(item)

    def getData(self):
        return self._data
