# -*- coding: utf-8 -*-
import logging
import warnings
import datetime

log = logging.getLogger(__name__)


class DocumentBaseRecord(object):
    """
    The base document class.

    Attributes:
        law_status (unicode): Key string of the law status.
        published_from (datetime.date): Date since this document was published.
        text_at_web (dict of uri): The multilingual URI to the documents content.
    """
    def __init__(self, law_status, published_from, text_at_web=None):
        """
        Args:
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date since this document was published.
            text_at_web (dict of uri): The multilingual URI to the documents content.
        """
        if text_at_web and not isinstance(text_at_web, dict):
            warnings.warn('Type of "text_at_web" should be "dict"')
        if published_from and not isinstance(published_from, datetime.date):
            warnings.warn('Type of "published_from" should be "datetime.date", not '
                          + str(type(published_from)))

        self.text_at_web = text_at_web
        self.law_status = law_status
        self.published_from = published_from

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
        log.debug("DocumentBaseRecord.published() returning {} for document {}"
                  .format(result, self.text_at_web))
        return result


class ArticleRecord(DocumentBaseRecord):
    """
    More specific document class representing articles.

    Attributes:
        law_status (unicode): Key string of the law status.
        published_from (datetime.date): Date since this document was published.
        number (unicode): The identifier of the article as a law.
        text_at_web (dict of uri): The URI to the documents content (multilingual).
        text (dict of unicode): Text in the article (multilingual).
    """
    def __init__(self, law_status, published_from, number, text_at_web=None, text=None):
        """
        Args:
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date since this document was published.
            number (unicode): The identifier of the article as a law.
            text_at_web (dict of uri): The URI to the documents content (multilingual).
            text (dict of unicode): Text in the article (multilingual).
        """
        super(ArticleRecord, self).__init__(law_status, published_from, text_at_web)

        if text and not isinstance(text, dict):
            warnings.warn('Type of "text" should be "dict"')
        if published_from and not isinstance(published_from, datetime.date):
            warnings.warn('Type of "published_from" should be "datetime.date", not '
                          + str(type(published_from)))

        self.number = number
        self.text = text


class DocumentRecord(DocumentBaseRecord):
    """
    More specific document class representing real documents.

    Attributes:
        document_type (str or unicode): The document type. It must be "LegalProvision", "Law" or "Hint"
                every other value will raise an error.
        law_status (unicode):  Key string of the law status.
        published_from (datetime.date): Date since this document was published.
        title (dict of unicode): The multilingual title of the document. It might be shortened one.
        responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
            responsible for this document.
        text_at_web (dict of uri): The multilingual URI to the documents content.
        official_title (dict of unicode): The official title of the document (multilingual).
        abbreviation (dict of unicode): Short term for this document (multilingual).
        official_number (unicode): The official number for identification of this document.
        canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
        municipality (unicode): The code for the municipality.
        article_numbers (list of unicode): Pointers to specific articles.
        file (bytes): The binary content of the document.
        articles (list of ArticleRecord): The linked articles.
        references (list of DocumentRecord): The references to other documents.
    """
    def __init__(self, document_type, law_status, published_from, title, responsible_office, text_at_web=None,
                 abbreviation=None, official_number=None, official_title=None, canton=None,
                 municipality=None, article_numbers=None, file=None, articles=None, references=None):
        """

        Args:
            document_type (str or unicode): The document type. It must be "LegalProvision", "Law" or "Hint"
                every other value will raise an error.
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date since this document was published.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            official_title (dict of unicode): The official title of the document (multilingual).
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (unicode): The official number for identification of this document.
            canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
            municipality (unicode): The code for the municipality.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
        super(DocumentRecord, self).__init__(law_status, published_from, text_at_web)

        if document_type != u'LegalProvision' and document_type != u'Law' and document_type != u'Hint':
            raise AttributeError('wrong value for document typ was delivered. Only "LegalProvision", '
                                 '"Law" and "Hint" are allowed. Value was {0}'.format(document_type))
        if not isinstance(title, dict):
            warnings.warn('Type of "title" should be "dict"')
        if official_title and not isinstance(official_title, dict):
            warnings.warn('Type of "official_title" should be "dict"')
        if abbreviation and not isinstance(abbreviation, dict):
            warnings.warn('Type of "abbreviation" should be "dict"')
        if published_from and not isinstance(published_from, datetime.date):
            warnings.warn('Type of "published_from" should be "datetime.date", not '
                          + str(type(published_from)))

        self.document_type = document_type
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
    """
        More specific document record class representing legal provision records.

        Attributes:
            document_type (str or unicode): The document type. Always "LegalProvision" for legal
                provision records.
            law_status (unicode):  Key string of the law status.
            published_from (datetime.date): Date since this document was published.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            official_title (dict of unicode): The official title of the document (multilingual).
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (unicode): The official number for identification of this document.
            canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
            municipality (unicode): The code for the municipality.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
    def __init__(self, law_status, published_from, title, responsible_office, text_at_web=None,
                 abbreviation=None, official_number=None, official_title=None, canton=None,
                 municipality=None, article_numbers=None, file=None, articles=None, references=None):
        """

        Args:
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date since this document was published.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            official_title (dict of unicode): The official title of the document (multilingual).
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (unicode): The official number for identification of this document.
            canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
            municipality (unicode): The code for the municipality.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
        super(LegalProvisionRecord, self).__init__('LegalProvision', law_status, published_from, title,
                                                   responsible_office, text_at_web,
                                                   abbreviation, official_number, official_title, canton,
                                                   municipality, article_numbers, file, articles, references)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class LawRecord(DocumentRecord):
    """
        More specific document record class representing law records.

        Attributes:
            document_type (str or unicode): The document type. Always "Law" for legal
                provision records.
            law_status (unicode):  Key string of the law status.
            published_from (datetime.date): Date since this document was published.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            official_title (dict of unicode): The official title of the document (multilingual).
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (unicode): The official number for identification of this document.
            canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
            municipality (unicode): The code for the municipality.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
    def __init__(self, law_status, published_from, title, responsible_office, text_at_web=None,
                 abbreviation=None, official_number=None, official_title=None, canton=None,
                 municipality=None, article_numbers=None, file=None, articles=None, references=None):
        """

        Args:
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date since this document was published.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            official_title (dict of unicode): The official title of the document (multilingual).
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (unicode): The official number for identification of this document.
            canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
            municipality (unicode): The code for the municipality.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
        super(LawRecord, self).__init__('Law', law_status, published_from, title,
                                        responsible_office, text_at_web,
                                        abbreviation, official_number, official_title, canton,
                                        municipality, article_numbers, file, articles, references)


class HintRecord(DocumentRecord):
    """
        More specific document record class representing hint records.

        Attributes:
            document_type (str or unicode): The document type. Always "Hint" for legal
                provision records.
            law_status (unicode):  Key string of the law status.
            published_from (datetime.date): Date since this document was published.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            official_title (dict of unicode): The official title of the document (multilingual).
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (unicode): The official number for identification of this document.
            canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
            municipality (unicode): The code for the municipality.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
    def __init__(self, law_status, published_from, title, responsible_office, text_at_web=None,
                 abbreviation=None, official_number=None, official_title=None, canton=None,
                 municipality=None, article_numbers=None, file=None, articles=None, references=None):
        """

        Args:
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date since this document was published.
            title (dict of unicode): The multilingual title of the document. It might be shortened one.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this document.
            text_at_web (dict of uri): The multilingual URI to the documents content.
            official_title (dict of unicode): The official title of the document (multilingual).
            abbreviation (dict of unicode): Short term for this document (multilingual).
            official_number (unicode): The official number for identification of this document.
            canton (unicode): The cantonal short term (length of two, like 'NE' or 'BL')
            municipality (unicode): The code for the municipality.
            article_numbers (list of unicode): Pointers to specific articles.
            file (bytes): The binary content of the document.
            articles (list of ArticleRecord): The linked articles.
            references (list of DocumentRecord): The references to other documents.
        """
        super(HintRecord, self).__init__('Hint', law_status, published_from, title,
                                         responsible_office, text_at_web,
                                         abbreviation, official_number, official_title, canton,
                                         municipality, article_numbers, file, articles, references)
