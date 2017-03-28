# -*- coding: utf-8 -*-

__author__ = 'François Voisard'
__create_date__ = '27.03.2017'


class ReferenceDefinitionRecord(object):

    def __init__(self, topic=None, canton=None, municipality=None, responsible_office=None, documents=list()):
        """
        Reference definition record. Definition of references which are independent from a restriction.
        :param topic: PLR topic if the reference relates to a specific topic
        :type  topic: str
        :param canton: Abbreviation of the canton if the reference concernes a specific canton
        :type  canton: str
        :param municipality: Name of the municipality if the reference relates to one
        :type municipality: str
        :param responsible_office: Office which is responsible for this reference.
        :type responsible_office: pyramid_oereb.lib.records.office.OfficeRecord
        :param documents: List of documents associated with this record.
        :type documents: list of pyramid_oereb.lib.records.documents.DocumentBaseRecord
        """

        if not (topic or canton or municipality and responsible_office):
            raise TypeError('At least one of the fields "topic", "canton" or "municipality" '
                            'and "responsible_office" must be defined. Got {0}, {1}, {2}, {3} .'
                            .format(topic, canton, municipality, responsible_office))

        self.topic = topic
        self.canton = canton
        self.municipality = municipality
        self.responsible_office = responsible_office
        self.documents = documents

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list
        """

        return [
            'topic',
            'canton',
            'municipality',
            'responsible_office',
            'documents'
        ]
