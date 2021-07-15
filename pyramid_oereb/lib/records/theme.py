# -*- coding: utf-8 -*-
import warnings


class ThemeRecord(object):
    """Creates a new theme record."""

    def __init__(self, code, title, extract_index):
        """
        Args:
            code (unicode): The theme's code.
            title (dict of unicode): The multilingual description.
            extract_index (int): Index to sort themes in the extract
        """
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')

        self.code = code
        self.title = title
        self.extract_index = extract_index

    def __str__(self):
        return '<{} -- code: {} title: {} extract index: {}>'.format(
            self.__class__.__name__, self.code, self.title, self.extract_index)
