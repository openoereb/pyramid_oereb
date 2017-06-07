# -*- coding: utf-8 -*-
import warnings


class ExclusionOfLiabilityRecord(object):

    def __init__(self, title, content):
        """
        Represents a exclusion of liability entry with the label and it's message.

        :param title: The multilingual disclaimer message label
        :type title: dict
        :param content: The multilingual disclaimer message.
        :type content: dict
        """
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict"')

        self.title = title
        self.content = content
