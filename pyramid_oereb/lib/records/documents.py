# -*- coding: utf-8 -*-
import logging
import warnings
import datetime

log = logging.getLogger(__name__)


class DocumentRecord(object):
    """
    More specific document class representing real documents.

    Attributes:
        document_type (str or unicode): The document type. It must be "LegalProvision", "Law" or "Hint"
                every other value will raise an error.
        index (int): An index used to sort the documents.
        law_status (unicode):  Key string of the law status.
        title (dict of unicode): The multilingual title of the document. It might be shortened one.
        responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
            responsible for this document.
        published_from (datetime.date): Date since this document was published.
        text_at_web (dict of uri): The multilingual URI to the documents content.
        abbreviation (dict of unicode): Short term for this document (multilingual).
        official_number (dict of unicode): The official number for identification of this document.
        only_in_municipality (int): Restrict document to a specific municipality by code.
        article_numbers (list of unicode): Pointers to specific articles.
        file (bytes): The binary content of the document.
    """
    def __init__(self, document_type, index, law_status, title, responsible_office, published_from,
                 text_at_web=None, abbreviation=None, official_number=None, only_in_municipality=None,
                 article_numbers=None, file=None):
        """

        Args:
            document_type (str or unicode): The document type. It must be "LegalProvision", "Law" or "Hint"
                every other value will raise an error.
            index (int): An index used to sort the documents.
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            published_from (datetime.date): Date since this document was published.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (dict of unicode): The official number for identification of this document.
            only_in_municipality (int): Restrict document to a specific municipality by code.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
        """

        if document_type not in ['Rechtsvorschrift', 'GesetzlicheGrundlage', 'Hinweis']:
            raise AttributeError('Wrong value for document type was delivered. Only "Rechtsvorschrift", '
                                 '"GesetzlicheGrundlage" and "Hinweis" are allowed. '
                                 'Value was {0}'.format(document_type))
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if abbreviation and not isinstance(abbreviation, dict):
            warnings.warn('Type of "abbreviation" should be "dict"')
        if official_number and not isinstance(official_number, dict):
            warnings.warn('Type of "official_number" should be "dict"')
        if published_from and not isinstance(published_from, datetime.date):
            warnings.warn('Type of "published_from" should be "datetime.date", not '
                          + str(type(published_from)))
        if text_at_web and not isinstance(text_at_web, dict):
            warnings.warn('Type of "text_at_web" should be "dict"')
        if published_from and not isinstance(published_from, datetime.date):
            warnings.warn('Type of "published_from" should be "datetime.date", not '
                          + str(type(published_from)))

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
        if isinstance(article_numbers, list):
            self.article_numbers = article_numbers
        else:
            self.article_numbers = []
        self.file = file

    @property
    def published(self):
        """
        Returns true if its not a future document.

        Returns:
            bool: True if document is published.
        """
        if isinstance(self.published_from, datetime.date):
            result = not self.published_from > datetime.date.today()
        else:
            result = not self.published_from > datetime.datetime.now()
        log.debug("DocumentRecord.published() returning {} for document {}"
                  .format(result, self.text_at_web))
        return result

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
