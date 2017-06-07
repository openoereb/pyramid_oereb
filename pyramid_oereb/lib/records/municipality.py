# -*- coding: utf-8 -*-


class MunicipalityRecord(object):

    def __init__(self, fosnr, name, published, logo, geom=None):
        """
        The record class for municipalities.

        :param fosnr: The unique id bfs of the municipality.
        :type fosnr: int
        :param name: The zipcode for this address.
        :type name: unicode
        :param published: Is this municipality ready for publishing via server.
        :type published: bool
        :param logo: The municipality logo.
        :type logo: pyramid_oereb.lib.records.image.ImageRecord
        :param geom: The geometry which is representing this municipality as a WKT.
        :type geom: str or None
        """
        self.fosnr = fosnr
        self.name = name
        self.published = published
        self.logo = logo
        self.geom = geom
