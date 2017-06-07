# -*- coding: utf-8 -*-
from datetime import datetime


class DocumentBaseRecord(object):

    def __init__(self, legal_state, published_from, text_at_web=None):
        """
        The base document class.

        :param legal_state: Key string of the law status.
        :type legal_state: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param text_at_web: The multilingual URI to the documents content.
        :type text_at_web: dict
        """
        self.text_at_web = text_at_web
        self.legal_state = legal_state
        self.published_from = published_from

    @property
    def published(self):
        """
        Returns true if its not a future document.

        :return: True if document is published.
        :rtype: bool
        """
        return not self.published_from > datetime.now().date()


class ArticleRecord(DocumentBaseRecord):

    def __init__(self, legal_state, published_from, number, text_at_web=None, text=None):
        """
        More specific document class representing articles.

        :param legal_state: Key string of the law status.
        :type legal_state: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param number: The identifier of the article as a law.
        :type number: str
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        :param text: Text in the article (multilingual).
        :type text: dict
        """
        super(ArticleRecord, self).__init__(legal_state, published_from, text_at_web)
        self.number = number
        self.text = text


class DocumentRecord(DocumentBaseRecord):

    def __init__(self, legal_state, published_from, title, responsible_office, text_at_web=None,
                 abbreviation=None, official_number=None, official_title=None, canton=None,
                 municipality=None, article_numbers=None, file=None, articles=None, references=None):
        """
        More specific document class representing real documents.

        :param legal_state:  Key string of the law status.
        :type legal_state: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param title: The multilingual title of the document. It might be shortened one.
        :type title: dict
        :param responsible_office: Office which is responsible for this document.
        :type responsible_office: pyramid_oereb.lib.records.office.OfficeRecord
        :param text_at_web: The multilingual URI to the documents content.
        :type text_at_web: dict
        :param official_title: The official title of the document (multilingual).
        :type official_title: dict
        :param abbreviation: Short term for this document (multilingual).
        :type abbreviation: dict
        :param official_number: The official number for identification of this document.
        :type official_number: str
        :param canton: The cantonal short term (length of tw, like: 'NE' or 'BL')
        :type canton: str
        :param municipality: The code for the municipality.
        :type municipality: str
        :param article_numbers: Pointers to specific articles.
        :type article_numbers: list of str
        :param file: The binary content of the document.
        :type file: bytes
        :param articles: The linked articles.
        :type articles: list of ArticleRecord
        :param references: The references to other documents.
        :type references: list of DocumentRecord
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


class LegalProvisionRecord(DocumentRecord):
    pass
