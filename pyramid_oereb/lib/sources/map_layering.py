# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.map_layering import MapLayeringRecord


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

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        pass  # pragma: no cover
