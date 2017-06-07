# -*- coding: utf-8 -*-


class ExclusionOfLiabilityRecord(object):

    def __init__(self, title, content):
        """
        Represents a exclusion of liability entry with the label and it's message.

        Args:
            title (unicode): The disclaimer message label
            content (unicode): The disclaimer message.
        """
        self.title = title
        self.content = content

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'title',
            'content'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in self.get_fields():
            value = getattr(self, key)
            if value:
                extract[key] = value
        return extract
