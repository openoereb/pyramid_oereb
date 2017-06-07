# -*- coding: utf-8 -*-


class GlossaryRecord(object):

    def __init__(self, title, content):
        """
        Represents a glossary entry with the term and it's description.

        Args:
            title (unicode): The term used in the extract
            content (unicode): The description text for the glossary entry.
        """
        self.title = title
        self.content = content

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            listofstr: List of available field names.
        """
        return [
            'title',
            'content'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        Returns:
            dict: Dictionary with values for the extract.
        """
        extract = dict()
        for key in self.get_fields():
            value = getattr(self, key)
            if value:
                extract[key] = value
        return extract
