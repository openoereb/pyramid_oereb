# -*- coding: utf-8 -*-
import warnings


class ThemeRecord(object):

    def __init__(self, code, text):
        """
        Creates a new theme record.

        Args:
            code (unicode): The theme's code.
            text (dict of unicode): The multilingual description.
        """
        if not isinstance(text, dict):
            warnings.warn('Type of "text" should be "dict"')

        self.code = code
        self.text = text
