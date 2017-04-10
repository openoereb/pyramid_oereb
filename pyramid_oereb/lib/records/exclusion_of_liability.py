# -*- coding: utf-8 -*-


class ExclusionOfLiabilityRecord(object):

    def __init__(self, title, content):
        """
        Represents a glossary entry with the term and it's description.
        :param title: The term used in the extract
        :type title: strint
        :param content: The description text for the glossary entry.
        :type content: str
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
