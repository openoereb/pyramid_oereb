# -*- coding: utf-8 -*-
import base64


class LogoRecord(object):

    def __init__(self, content):
        """
        The record to hold the binary information of a logo/image.

        Args:
            content (str): The binary information of this logo as binary string.
        """
        self.content = content

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            list of str: List of available field names.
        """
        return [
            'content'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        Returns:
            dict: Dictionary with values for the extract.
        """
        extract = dict()
        key = 'content'
        extract[key] = base64.b64encode(getattr(self, key))

        return extract

    def encode(self):
        """
        Returns the logo as base64 encoded string.

        Returns:
            str: The encoded image.
        """
        return base64.b64encode(self.content)
