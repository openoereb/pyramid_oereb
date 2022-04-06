# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.municipality import MunicipalityRecord


class MunicipalityBaseSource(Base):
    """
    Base class for municipality sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.municipality.MunicipalityRecord): List of municipality
            records.
    """
    _record_class_ = MunicipalityRecord

    def read(self):
        """
        Every municipality source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for municipalities, this is the point where to hook in.
        """
        pass  # pragma: no cover
