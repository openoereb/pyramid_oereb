# -*- coding: utf-8 -*-


class MunicipalityRecord(object):

    def __init__(self, fosnr, name, published, logo, geom=None):
        """
        The base document class.
        :param fosnr: The unique id bfs of the municipality.
        :type fosnr: int
        :param name: The zipcode for this address.
        :type name: unicode
        :param published: Is this municipality ready for publishing via server.
        :type published: bool
        :param logo: The municipality logo.
        :type logo: pyramid_oereb.lib.records.logo.LogoRecord
        :param geom: The geometry which is representing this municipality as a WKT.
        :type geom: str or None
        """
        self.fosnr = fosnr
        self.name = name
        self.published = published
        self.logo = logo
        self.geom = geom

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'fosnr',
            'name',
            'published',
            'logo',
            'geom'
        ]
