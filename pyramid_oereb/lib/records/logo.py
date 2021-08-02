# -*- coding: utf-8 -*-
import warnings


class LogoRecord(object):
    """
    Represents a logo with its code and its base64 encoded string (multilingual).

    Args:
        code (str of unicode): The code for the logo.
        logo (dict of unicode): The image encoded as base64 (multilingual).
    """
    def __init__(self, code, logo):

        if not isinstance(code, str):
            warnings.warn('Type of "code" should be "str"')
        if not isinstance(logo, dict):
            warnings.warn('Type of "logo" should be "dict"')

        self.code = code
        self.logo = logo
