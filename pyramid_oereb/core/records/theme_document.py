# -*- coding: utf-8 -*-


class ThemeDocumentRecord(object):
    """Creates a new theme record.
    Attributes:
        theme_id (str): Foreign key relating to theme's id.
        document_id (str): Foreign key relating to document's id.
        article_numbers (list of str): Article numbers to refine statement of document to a theme.
    """

    def __init__(self, theme_id, document_id, article_numbers):
        """
        Args:
            theme_id (str): Foreign key relating to theme's id.
            document_id (str): Foreign key relating to document's id.
            article_numbers (list of str): Article numbers to refine statement of document to a theme.
        """

        self.theme_id = theme_id
        self.document_id = document_id
        self.article_numbers = article_numbers

    def __str__(self):
        return '<{} -- theme_id: {} document_id: {}>'.format(
            self.__class__.__name__, self.theme_id, self.document_id)
