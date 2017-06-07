# -*- coding: utf-8 -*-


class ReferenceDefinitionRecord(object):

    def __init__(self, topic, canton, municipality, responsible_office, documents=None):
        """
        Reference definition record. Definition of references which are independent from a restriction.

        Args:
            topic (str): PLR topic if the reference relates to a specific topic
            canton (str): Abbreviation of the canton if the reference concernes a specific
                canton
            municipality (str): Name of the municipality if the reference relates to one
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this reference.
            documents (listofpyramid_oereb.lib.records.documents.DocumentBaseRecord): List of
                documents associated with this record.
        """

        self.topic = topic
        self.canton = canton
        self.municipality = municipality
        self.responsible_office = responsible_office
        if documents is None:
            self.documents = []
        else:
            self.documents = documents

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            list: List of available field names.
        """

        return [
            'topic',
            'canton',
            'municipality',
            'responsible_office',
            'documents'
        ]
