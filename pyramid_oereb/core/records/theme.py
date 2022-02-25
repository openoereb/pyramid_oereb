# -*- coding: utf-8 -*-
import warnings


class ThemeRecord(object):
    """Creates a new theme record.
    Attributes:
        code (unicode): The theme's code.
        title (dict of unicode): The multilingual description.
        extract_index (int): Index to sort themes in the extract.
        sub_code (unicode): The code of the sub_theme. Is none for themes.
        document_records (list of str): Documents that relates to this theme
        identifier (str): The identifier of the theme which might be used for linking to other elements.

    """

    def __init__(self, code, title, extract_index, sub_code=None, document_records=None, identifier=None):
        """
        Args:
            code (unicode): The theme's code.
            title (dict of unicode): The multilingual description.
            extract_index (int): Index to sort themes in the extract.
            sub_code (unicode): The code of the sub_theme. Is none for themes.
            document_records (list of str): Documents that relates to this theme
            identifier (str): The identifier of the theme which might be used for linking to other elements.
        """
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')

        self.code = code
        self.sub_code = sub_code
        self.title = title
        self.extract_index = extract_index
        self.document_records = document_records
        self.identifier = identifier

    def __str__(self):
        return '<{} -- code: {} sub code: {} title: {} extract index: {} document records: {}>'.format(
            self.__class__.__name__, self.code, self.sub_code, self.title,
            self.extract_index, self.document_records)
