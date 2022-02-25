# -*- coding: utf-8 -*-
import warnings


class GlossaryRecord(object):
    """
    Represents a glossary entry with the term and it's description.

    Attributes:
        title (dict of unicode): The term used in the extract (multilingual).
        content (dict of unicode): The description text for the glossary entry (multilingual).
    """
    def __init__(self, title, content):
        """
        Args:
            title (dict of unicode): The term used in the extract (multilingual).
            content (dict of unicode): The description text for the glossary entry (multilingual)
        """

        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict"')

        self.title = title
        self.content = content
