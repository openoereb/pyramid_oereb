# -*- coding: utf-8 -*-


class ExclusionOfLiabilityRecord(object):

    def __init__(self, title, content):
        """
        Represents a exclusion of liability entry with the label and it's message.

        :param title: The multilingual disclaimer message label
        :type title: dict
        :param content: The multilingual disclaimer message.
        :type content: dict
        """
        self.title = title
        self.content = content
