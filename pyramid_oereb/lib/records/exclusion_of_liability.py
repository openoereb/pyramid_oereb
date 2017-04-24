# -*- coding: utf-8 -*-


class ExclusionOfLiabilityRecord(object):

    def __init__(self, id, title, content):
        """
        Represents a exclusion of liability entry with the label and it's message.
        :param id: The identifier in the database
        :type id: int
        :param title: The disclaimer message label 
        :type title: unicode
        :param content: The disclaimer message.
        :type content: unicode
        """
        self.id = id
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
            'id',
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

