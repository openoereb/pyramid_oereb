# -*- coding: utf-8 -*-
import warnings


class ThemeDocumentRecord(object):
    """Creates a new theme record."""

    def __init__(self, theme_id, document_id):
        """
        Args:
            theme_id (str): Foreign key relating to theme's id.
            document_id (str): Foreign key relating to document's id.
        """

        self.theme_id = theme_id
        self.document_id = document_id

    def __str__(self):
        return '<{} -- theme_id: {} document_id: {}>'.format(
            self.__class__.__name__, self.theme_id, self.document_id)
