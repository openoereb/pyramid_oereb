# -*- coding: utf-8 -*-
from datetime import datetime


class DocumentBaseRecord(object):

    def __init__(self, legal_state, published_from, text_at_web=None):
        """
        The base document class.

        Args:
            legal_state (str): Key string of the law status.
            published_from (datetime.date): Date since this document was published.
            text_at_web (str): The URI to the documents content.
        """
        self.text_at_web = text_at_web
        self.legal_state = legal_state
        self.published_from = published_from

    @property
    def published(self):
        """
        Returns true if its not a future document.

        Returns:
            bool: True if document is published.
        """
        return not self.published_from > datetime.now().date()

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            list of str: List of available field names.
        """
        return [
            'text_at_web',
            'legal_state',
            'published_from'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        Returns:
            dict: Dictionary with values for the extract.
        """
        extract = dict()
        for key in ['text_at_web', 'legal_state']:
            value = getattr(self, key)
            if value:
                extract[key] = value
        return extract


class ArticleRecord(DocumentBaseRecord):

    def __init__(self, legal_state, published_from, number, text_at_web=None, text=None):
        """
        More specific document class representing articles.

        Args:
            legal_state (str): Key string of the law status.
            published_from (datetime.date): Date since this document was published.
            number (str): The identifier of the article as a law.
            text_at_web (str): The URI to the documents content.
            text (str): Text in the article.
        """
        super(ArticleRecord, self).__init__(legal_state, published_from, text_at_web)
        self.number = number
        self.text = text

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            list of str: List of available field names.
        """
        return [
            'text_at_web',
            'legal_state',
            'published_from',
            'number',
            'text'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        Returns:
            dict: Dictionary with values for the extract.
        """
        extract = super(ArticleRecord, self).to_extract()
        for key in ['number', 'text']:
            value = getattr(self, key)
            if value:
                extract[key] = value
        return extract


class DocumentRecord(DocumentBaseRecord):

    def __init__(self, legal_state, published_from, title, responsible_office, text_at_web=None,
                 abbreviation=None, official_number=None, official_title=None, canton=None,
                 municipality=None, article_numbers=None, file=None, articles=None, references=None):
        """
        More specific document class representing real documents.

        Args:
            legal_state (str):  Key string of the law status.
            published_from (datetime.date): Date since this document was published.
            title (unicode): The title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (str): The URI to the documents content.
            official_title (unicode): The official title of the document.
            abbreviation (str): Short term for this document.
            official_number (str): The official number for identification of this document.
            canton (str): The cantonal short term (length of tw, like
            municipality (str): The code for the municipality.
            article_numbers (list of str): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
        super(DocumentRecord, self).__init__(legal_state, published_from, text_at_web)
        self.title = title
        self.responsible_office = responsible_office
        self.official_title = official_title
        self.abbreviation = abbreviation
        self.official_number = official_number
        self.canton = canton
        self.municipality = municipality
        if isinstance(article_numbers, list):
            self.article_numbers = article_numbers
        else:
            self.article_numbers = []
        self.file = file
        if articles is None:
            self.articles = []
        else:
            self.articles = articles
        if references is None:
            self.references = []
        else:
            self.references = references

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            list of str: List of available field names.
        """
        return [
            'text_at_web',
            'legal_state',
            'published_from',
            'title',
            'official_title',
            'responsible_office',
            'abbreviation',
            'official_number',
            'canton',
            'municipality',
            'article_numbers',
            'file',
            'articles',
            'references'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        Returns:
            dict: Dictionary with values for the extract.
        """
        extract = super(DocumentRecord, self).to_extract()

        for key in [
            'title',
            'official_title',
            'abbreviation',
            'official_number',
            'canton',
            'municipality',
            'file'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value

        for key in ['articles', 'references']:
            records = getattr(self, key)
            if records and len(records) > 0:
                extract[key] = [record.to_extract() for record in records]

        key = 'responsible_office'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract()

        key = 'article_numbers'
        value = getattr(self, key)
        if isinstance(value, list) and len(value) > 0:
            extract[key] = value

        return extract


class LegalProvisionRecord(DocumentRecord):
    pass
