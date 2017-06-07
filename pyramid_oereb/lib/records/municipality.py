# -*- coding: utf-8 -*-


class MunicipalityRecord(object):

    def __init__(self, fosnr, name, published, logo, geom=None):
        """
        The base document class.

        Args:
            fosnr (int): The unique id bfs of the municipality.
            name (unicode): The zipcode for this address.
            published (bool): Is this municipality ready for publishing via server.
            logo (pyramid_oereb.lib.records.logo.LogoRecord): The municipality logo.
            geom (strorNone): The geometry which is representing this municipality as a WKT.
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

        Returns:
            listofstr: List of available field names.
        """
        return [
            'fosnr',
            'name',
            'published',
            'logo',
            'geom'
        ]
