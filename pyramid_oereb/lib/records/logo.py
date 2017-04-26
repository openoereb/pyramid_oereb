# -*- coding: utf-8 -*-
import base64


class LogoRecord(object):

    def __init__(self, content):
        """
        The record to hold the binary information of a logo/image.
        :param content: The binary information of this logo as binary string.
        :type content: str
        """
        self.content = content

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'content'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        key = 'content'
        extract[key] = base64.b64encode(getattr(self, key))

        return extract
