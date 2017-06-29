# -*- coding: utf-8 -*-


class MunicipalityRecord(object):
    """
    The base document class.

    Args:
        fosnr (int): The unique id bfs of the municipality.
        name (unicode): The zipcode for this address.
        published (bool): Is this municipality ready for publishing via server.
        logo (pyramid_oereb.lib.records.image.ImageRecord): The municipality logo.
        geom (str or None): The geometry which is representing this municipality as a WKT.
    """
    def __init__(self, fosnr, name, published, logo, geom=None):
        self.fosnr = fosnr
        self.name = name
        self.published = published
        self.logo = logo
        self.geom = geom
