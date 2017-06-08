# -*- coding: utf-8 -*-


class ThemeRecord(object):

    def __init__(self, code, text):
        """
        Creates a new theme record.

        Args:
            code (str): The theme's code.
            text (dict): The multilingual description.
        """
        self.code = code
        self.text = text

    @classmethod
    def get_fields(cls):
        """
        Returns a listing of the record's fields.

        Returns:
            list of str: The available fields.
        """
        return [
            'code',
            'text'
        ]

    def to_extract(self):
        text = list()
        for k, v in self.text.iteritems():
            text.append({
                'language': k,
                'text': v
            })
        return {
            'code': self.code,
            'text': text
        }
