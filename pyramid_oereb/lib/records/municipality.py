# -*- coding: utf-8 -*-


class MunicipalityRecord(object):

    def __init__(self, id_bfs, name, published, geometry=None):
        """
        The base document class.
        :param id_bfs: The unique id bfs of the municipality.
        :type id_bfs: int
        :param name: The zipcode for this address.
        :type name: unicode
        :param published: Is this municipality ready for publishing via server.
        :type published: bool
        :param geometry: The geometry which is representing this municipality as a WKT.
        :type geometry: str or None
        """
        self.id_bfs = id_bfs
        self.name = name
        self.published = published
        self.geometry = geometry

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'id_bfs',
            'name',
            'published',
            'geometry'
        ]
