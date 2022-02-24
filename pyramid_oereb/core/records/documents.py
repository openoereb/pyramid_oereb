# -*- coding: utf-8 -*-
import logging
import warnings
import datetime

from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.document_types import DocumentTypeRecord


log = logging.getLogger(__name__)


class DocumentRecord(object):
    """
    More specific document class representing real documents.

    Attributes:
        document_type (pyramid_oereb.lib.records.document_types.DocumentTypeRecord): The document type.
        index (int): An index used to sort the documents.
        law_status (dict):  Multilingual label of the law status.
        title (dict of unicode): The multilingual title of the document. It might be shortened one.
        responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
            responsible for this document.
        published_from (datetime.date): Date from when this document is published.
        published_until (datetime.date): Date until when this document is published.
        text_at_web (dict of uri): The multilingual URI to the documents content.
        abbreviation (dict of unicode): Short term for this document (multilingual).
        official_number (dict of unicode): The official number for identification of this document.
        only_in_municipality (int): Restrict document to a specific municipality by code.
        article_numbers (list of unicode): Pointers to specific articles.
        file (bytes): The binary content of the document.
    """
    def __init__(self, document_type, index, law_status, title, responsible_office, published_from,
                 published_until=None, text_at_web=None, abbreviation=None, official_number=None,
                 only_in_municipality=None, article_numbers=None, file=None, identifier=None):
        """

        Args:
            document_type (pyramid_oereb.lib.records.document_types.DocumentTypeRecord): The document type.
            index (int): An index used to sort the documents.
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            published_from (datetime.date): Date from when this document is published.
            published_until (datetime.date): Date until when this document is published.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (dict of unicode): The official number for identification of this document.
            only_in_municipality (int): Restrict document to a specific municipality by code.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            identifier (str): The identifier of the document which might be used for linking to
                other elements.
        """

        if not isinstance(document_type, DocumentTypeRecord):
            raise AttributeError('Type of "document_type" must be '
                                 'pyramid_oereb.core.records.document_types.DocumentTypeRecord '
                                 'but was {0}'.format(type(document_type)))
        if not isinstance(index, int):
            warnings.warn('Type of "index" should be "int"')
        if not isinstance(law_status, LawStatusRecord):
            warnings.warn('Type of "law_status" should be '
                          '"pyramid_oereb.core.records.law_status.LawStatusRecord"')
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if not isinstance(responsible_office, OfficeRecord):
            warnings.warn('Type of "responsible_office" should be '
                          '"pyramid_oereb.core.records.office.OfficeRecord"')
        if not isinstance(published_from, datetime.date):
            warnings.warn('Type of "published_from" should be "datetime.date", not '
                          + str(type(published_from)))

        if published_until and not isinstance(published_until, datetime.date):
            warnings.warn('Type of "published_from" should be "datetime.date", not '
                          + str(type(published_until)))
        if text_at_web and not isinstance(text_at_web, dict):
            warnings.warn('Type of "text_at_web" should be "dict"')
        if abbreviation and not isinstance(abbreviation, dict):
            warnings.warn('Type of "abbreviation" should be "dict"')
        if official_number and not isinstance(official_number, dict):
            warnings.warn('Type of "official_number" should be "dict"')
        if only_in_municipality and not isinstance(only_in_municipality, int):
            warnings.warn('Type of "only_in_municipality" should be "int"')
        if article_numbers and not isinstance(article_numbers, list):
            warnings.warn('Type of "article_numbers" should be "list"')
        if file and not isinstance(file, bytes):
            warnings.warn('Type of "file" should be "bytes"')

        self.document_type = document_type
        self.title = title
        self.index = index
        self.responsible_office = responsible_office
        self.abbreviation = abbreviation
        self.official_number = official_number
        self.only_in_municipality = only_in_municipality
        self.text_at_web = text_at_web
        self.law_status = law_status
        self.published_from = published_from
        self.published_until = published_until
        if isinstance(article_numbers, list):
            self.article_numbers = article_numbers
        else:
            self.article_numbers = []
        self.file = file
        self.identifier = identifier

    @property
    def published(self):
        """
        Returns true if its not a future or past document.

        Returns:
            bool: True if document is published.
        """
        result = True

        # Check for published_from
        if isinstance(self.published_from, datetime.datetime):
            if datetime.datetime.now() < self.published_from:
                result = False
        elif isinstance(self.published_from, datetime.date):
            if datetime.date.today() < self.published_from:
                result = False

        # Check for published_until
        if isinstance(self.published_until, datetime.datetime):
            if datetime.datetime.now() > self.published_until:
                result = False
        elif isinstance(self.published_until, datetime.date):
            if datetime.date.today() > self.published_until:
                result = False

        log.debug("DocumentRecord.published() returning {} for document {}"
                  .format(result, self.text_at_web))
        return result

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def copy(self):
        """
        Returns (DocumentRecord): A copy of this DocumentRecord element
        """
        return DocumentRecord(
            self.document_type,
            self.index,
            self.law_status,
            self.title,
            self.responsible_office,
            self.published_from,
            published_until=self.published_until,
            text_at_web=self.text_at_web,
            abbreviation=self.abbreviation,
            official_number=self.official_number,
            only_in_municipality=self.only_in_municipality,
            article_numbers=self.article_numbers,
            file=self.file,
            identifier=self.identifier
        )
