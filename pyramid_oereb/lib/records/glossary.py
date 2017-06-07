# -*- coding: utf-8 -*-
import warnings


class GlossaryRecord(object):

    def __init__(self, title, content):
        """
        Represents a glossary entry with the term and it's description.

        :param title: The term used in the extract (multilingual).
        :type title: dict
        :param content: The description text for the glossary entry (multilingual).
        :type content: dict
        """
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict"')

        self.title = title
        self.content = content
