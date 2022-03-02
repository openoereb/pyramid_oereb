# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.map_layering import MapLayeringRecord


class MapLayeringBaseSource(Base):
    """
    Base class for address sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.map_layering.MapLayeringRecord):
            List of map layering records.
    """
    _record_class_ = MapLayeringRecord

    def read(self):
        """
        Every map layering source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for map layering, this is the point where to hook in.
        """
        pass  # pragma: no cover
