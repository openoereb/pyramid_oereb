# -*- coding: utf-8 -*-


class DocumentBaseRecord(object):

    def __init__(self, law_status=None, published_from=None, text_at_web=None):
        """
        The base document class.
        :param law_status: Key string of the law status.
        :type law_status: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        """
        if not (law_status and published_from):
            raise TypeError('Fields "law_status", "published_from" must be defined. '
                            'Got {0}, {1}.'.format(law_status, published_from))
        self.text_at_web = text_at_web
        self.law_status = law_status
        self.published_from = published_from

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'text_at_web',
            'law_status',
            'published_from'
        ]


class ArticleRecord(DocumentBaseRecord):

    def __init__(self, law_status=None, published_from=None, number=None, text_at_web=None, text=None):
        """
        More specific document class representing articles.
        :param law_status: Key string of the law status.
        :type law_status: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param number: The identifier of the article as a law.
        :type number: str
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        :param text: Text in the article.
        :type text: str
        """
        super(ArticleRecord, self).__init__(law_status, published_from, text_at_web)
        if not number:
            raise TypeError('Field "number" must be defined. '
                            'Got {0}.'.format(number))
        self.number = number
        self.text = text

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'text_at_web',
            'law_status',
            'published_from',
            'number',
            'text'
        ]


class DocumentRecord(DocumentBaseRecord):

    def __init__(self, law_status=None, published_from=None, title=None, responsible_office=None,
                 text_at_web=None, official_title=None, abbreviation=None, official_number=None, canton=None,
                 municipality=None, file=None, articles=None, references=None):
        """
        More specific document class representing real documents.
        :param law_status:  Key string of the law status.
        :type law_status: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        :param title: The title of the document. It might be shortened one.
        :type title: str
        :param responsible_office: Office which is responsible for this document.
        :type responsible_office: pyramid_oereb.lib.records.office.OfficeRecord
        :param official_title: The official title of the document.
        :type official_title: str
        :param abbreviation: Short term for this document.
        :type abbreviation: str
        :param official_number: The official number for identification of this document.
        :type official_number: str
        :param canton: The cantonal short term (length of tw, like: 'NE' or 'BL')
        :type canton: str
        :param municipality: The code for the municipality.
        :type municipality: str
        :param file: The binary content of the document.
        :type file: bytes
        :param articles: The linked articles.
        :type articles: list of ArticleRecord
        :param references: The references to other documents.
        :type references: list of DocumentRecord
        """
        super(DocumentRecord, self).__init__(law_status, published_from, text_at_web)
        if not (title and responsible_office):
            raise TypeError('Fields "title" and "responsible_office" must be defined. '
                            'Got {0} and {1}.'.format(title, responsible_office))
        self.title = title
        self.responsible_office = responsible_office
        self.official_title = official_title
        self.abbreviation = abbreviation
        self.official_number = official_number
        self.canton = canton
        self.municipality = municipality
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
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'text_at_web',
            'law_status',
            'published_from',
            'title',
            'responsible_office',
            'abbreviation',
            'official_number',
            'canton',
            'municipality',
            'file',
            'articles',
            'references'
        ]


class LegalProvisionRecord(DocumentRecord):
    pass
