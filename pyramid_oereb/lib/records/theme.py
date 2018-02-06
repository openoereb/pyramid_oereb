# -*- coding: utf-8 -*-
import warnings


class ThemeRecord(object):
    """Creates a new theme record."""

    def __init__(self, code, text):
        """
        Args:
            code (unicode): The theme's code.
            text (dict of unicode): The multilingual description.
            data_owner (pyramid_oereb.lib.records.office.OfficeRecord):
            transfer_from_source (datetime.date): The actuality of the themes data
        """
        if not isinstance(text, dict):
            warnings.warn('Type of "text" should be "dict"')

        self.code = code
        self.text = text

    def __str__(self):
        return '<{} -- code: {} text: {}>'.format(self.__class__.__name__, self.code, self.text)
