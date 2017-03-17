# -*- coding: utf-8 -*-


class Base(object):
    records = list()

    def __init__(self):
        """
        Base class for all sources.
        """
        pass

    def read(self):
        """
        Every source class has to implement a read method.
        """
        pass  # pragma: no cover
