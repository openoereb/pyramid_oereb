# -*- coding: utf-8 -*-

__author__ = 'François Voisard'
__create_date__ = '27.03.2017'


class ReferenceDefinitionRecord(object):
    topic = None
    canton = None
    municipality = None

    def __init__(self, topic=None, canton=None, municipality=None):
        """
        Reference definition record. Definition of references which are independent from a restriction.
        :param topic: PLR topic if the reference relates to a specific topic
        :type  topic: str
        :param canton: Abbreviation of the canton if the reference concernes a specific canton
        :type  canton: str
        :param municipality: Name of the municipality if the reference relates to one
        :type municipality: str
        """

        if not (topic or canton or municipality):
            raise TypeError('At least one of the fields "topic", "canton" or "municipality" must be defined. '
                            'Got {0}, {1}, {2} .'.format(topic, canton, municipality))

        self.topic = topic
        self.canton = canton
        self.municipality = municipality

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
            'municipality'
        ]
