# -*- coding: utf-8 -*-


class DocumentBaseRecord(object):

    def __init__(self, legal_state, published_from, text_at_web=None):
        """
        The base document class.
        :param legal_state: Key string of the law status.
        :type legal_state: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        """
        self.text_at_web = text_at_web
        self.legal_state = legal_state
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
            'legal_state',
            'published_from'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
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
        :param legal_state: Key string of the law status.
        :type legal_state: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param number: The identifier of the article as a law.
        :type number: str
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        :param text: Text in the article.
        :type text: str
        """
        super(ArticleRecord, self).__init__(legal_state, published_from, text_at_web)
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
            'legal_state',
            'published_from',
            'number',
            'text'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
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
        :param legal_state:  Key string of the law status.
        :type legal_state: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param title: The title of the document. It might be shortened one.
        :type title: unicode
        :param responsible_office: Office which is responsible for this document.
        :type responsible_office: pyramid_oereb.lib.records.office.OfficeRecord
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        :param official_title: The official title of the document.
        :type official_title: unicode
        :param abbreviation: Short term for this document.
        :type abbreviation: str
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

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
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
        :return: Dictionary with values for the extract.
        :rtype: dict
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
