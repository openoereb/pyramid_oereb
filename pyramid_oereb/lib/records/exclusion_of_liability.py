# -*- coding: utf-8 -*-
import warnings


class ExclusionOfLiabilityRecord(object):

    def __init__(self, title, content):
        """
        Represents a exclusion of liability entry with the label and it's message.

        Args:
            title (dict of unicode): The multilingual disclaimer message label
            content (dict of unicode): The multilingual disclaimer message.
        """
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict"')

        self.title = title
        self.content = content
