# -*- coding: utf-8 -*-


class ThemeRecord(object):

    def __init__(self, code, text):
        """
        Creates a new theme record.

        :param code: The theme's code.
        :type code: str
        :param text: The multilingual description.
        :type text: dict
        """
        self.code = code
        self.text = text
