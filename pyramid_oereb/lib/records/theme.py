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

    @classmethod
    def get_fields(cls):
        """
        Returns a listing of the record's fields.

        :return: The available fields.
        :rtype: list of str
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
