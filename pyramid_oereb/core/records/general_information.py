# -*- coding: utf-8 -*-
import warnings


class GeneralInformationRecord(object):
    """
    Represents a general information entry with its title and content.
    Attributes:
        title (dict of unicode): The title of the information (multilingual)
        content (dict of unicode): The actual information (multilingual)
    """
    def __init__(self, title, content):
        """
        Args:
            title (dict of unicode): The title of the information (multilingual)
            content (dict of unicode): The actual information (multilingual)
        """

        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict"')

        self.title = title
        self.content = content

    def __str__(self):
        return '<{} -- title: {} content: {}>'.format(
            self.__class__.__name__, self.title, self.content)
