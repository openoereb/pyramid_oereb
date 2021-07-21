# -*- coding: utf-8 -*-
import warnings


class RealEstateTypeRecord(object):
    """
    Represents a real estate type entry with the code and it's display name.
    Args:
        code (str of unicode): The code for the real estate type (Property, Building right,
        Right to spring water).
        text (dict of unicode): The label text for the real estate type (multilingual).
    """
    def __init__(self, code, text):

        if not isinstance(code, str):
            warnings.warn('Type of "code" should be "str"')
        if not isinstance(text, dict):
            warnings.warn('Type of "text" should be "dict"')

        self.code = code
        self.text = text
