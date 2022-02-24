# -*- coding: utf-8 -*-


class MunicipalityRecord(object):
    """
    The base document class.

    Attributes:
        fosnr (int): The unique id bfs of the municipality.
        name (unicode): The zipcode for this address.
        published (bool): Is this municipality ready for publishing via server.
        geom (str or None): The geometry which is representing this municipality as a WKT.
    """
    def __init__(self, fosnr, name, published, geom=None):
        """
        Args:
            fosnr (int): The unique id bfs of the municipality.
            name (unicode): The zipcode for this address.
            published (bool): Is this municipality ready for publishing via server.
            geom (str or None): The geometry which is representing this municipality as a WKT.
        """
        self.fosnr = fosnr
        self.name = name
        self.published = published
        self.geom = geom
