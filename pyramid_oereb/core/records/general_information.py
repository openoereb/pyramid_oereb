# -*- coding: utf-8 -*-
import warnings


class GeneralInformationRecord(object):
    """
    Represents a general information entry with its title and content.
    Attributes:
        title (dict of unicode): The title of the information (multilingual)
        content (dict of unicode): The actual information (multilingual)
    """
    def __init__(self, title, content, extract_index=None):
        """
        Args:
            title (dict of unicode): The title of the information (multilingual)
            content (dict of unicode): The actual information (multilingual)
        """

        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict", is {}, value {}'
                          .format(type(title), title))

        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict", is {}, value {}'
                          .format(type(content), content))

        self.title = title
        self.content = content
        self.extract_index = extract_index

    def __str__(self):
        return '<{} -- title: {} content: {} extract index: {}>'.format(
            self.__class__.__name__, self.title, self.content, self.extract_index)
