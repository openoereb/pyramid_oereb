# -*- coding: utf-8 -*-


class GlossaryRecord(object):

    def __init__(self, title, content):
        """
        Represents a glossary entry with the term and it's description.
        :param title: The term used in the extract
        :type title: unicode
        :param content: The description text for the glossary entry.
        :type content: unicode
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
