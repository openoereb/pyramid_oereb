# -*- coding: utf-8 -*-
import warnings


class RealEstateTypeRecord(object):
    """
    Represents a real estate type entry with the code and it's display name.
    Attributes:
        code (str of unicode): The code for the real estate type.
        title (dict of unicode): The label title for the real estate type (multilingual).
    """
    def __init__(self, code, title):
        """
        Args:
            code (str of unicode): The code for the real estate type.
            title (dict of unicode): The label title for the real estate type (multilingual).
        """

        if not isinstance(code, str):
            warnings.warn('Type of "code" should be "str"')
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        self.code = code
        self.title = title
