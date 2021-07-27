# -*- coding: utf-8 -*-
import warnings


class Logo(object):
    """
    Represents a logo with its code and its base64 encoded string (multilingual).

    Args:
        code (str of unicode): The code for the logo.
        text (dict of unicode): The image encoded as base64 (multilingual).
    """
    def __init__(self, code, text):

        if not isinstance(code, str):
            warnings.warn('Type of "code" should be "str"')
        if not isinstance(text, dict):
            warnings.warn('Type of "text" should be "dict"')

        self.code = code
        self.text = text
