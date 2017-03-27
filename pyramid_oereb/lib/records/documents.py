# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2016, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
# All rights reserved.
#
# This program is free software and completes the GeoMapFish License for the geoview.bl.ch specific
# parts of the code. You can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.

__author__ = 'Clemens Rudert'
__create_date__ = '27.03.17'


class DocumentBase(object):

    def __init__(self, law_status, published_from, text_at_web=None):
        """
        The base document class.
        :param law_status: Key string of the law status.
        :type law_status: str
        :param published_from: Date since this document was published.
        :type published_from: datetime.date
        :param text_at_web: The URI to the documents content.
        :type text_at_web: str
        """
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


class Article(DocumentBase):

    def __init__(self, law_status, published_from, number, text_at_web=None, text=None):
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
        super(Article, self).__init__(law_status, published_from, text_at_web)
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


class Document(DocumentBase):

    def __init__(self, law_status, published_from, text_at_web, title, responsible_office,
                 official_title=None, abbrevation=None, official_number=None, canton=None, municipality=None,
                 file=None, articles=None, references=None):
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
        :type responsible_office: pyramid_oereb.lib.records.office.Office
        :param official_title: The official title of the document.
        :type official_title: str
        :param abbrevation: Short term for this document.
        :type abbrevation: str
        :param official_number: The official number for identification of this document.
        :type official_number: str
        :param canton: The cantonal short term (length of tw, like: 'NE' or 'BL')
        :type canton: str
        :param municipality: The code for the municipality.
        :type municipality: str
        :param file: The binary content of the document.
        :type file: bytes
        :param articles: The linked articles.
        :type articles: list of Article
        :param references: The references to other documents.
        :type references: list of Document
        """
        super(Document, self).__init__(law_status, published_from, text_at_web)
        self.title = title
        self.responsible_office = responsible_office
        self.official_title = official_title
        self.abbrevation = abbrevation
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
            'abbrevation',
            'official_number',
            'canton',
            'municipality',
            'file',
            'articles',
            'references'
        ]


class LegalProvision(Document):
    pass
