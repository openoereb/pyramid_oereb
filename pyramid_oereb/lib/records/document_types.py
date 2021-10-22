# -*- coding: utf-8 -*-
import warnings


class DocumentTypeRecord(object):

    """
    Represents a document type entry with the code and it's display name.

    Args:
        code (str of unicode): The code for the document type.
        title (dict of unicode): The label title for the document type (multilingual).
    """
    def __init__(self, code, title):
        if not isinstance(code, str):
            warnings.warn('Type of "code" should be "str"')
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')

        self.code = code
        self.title = title
