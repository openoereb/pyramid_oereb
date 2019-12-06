# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.municipality import MunicipalityRecord


class MunicipalityBaseSource(Base):
    """
    Base class for municipality sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.municipality.MunicipalityRecord): List of municipality
            records.
    """
    _record_class_ = MunicipalityRecord

    def read(self, fosnr=None):
        """
        Every municipality source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for municipalities, this is the point where to hook in.

        Args:
            fosnr (int or None): The federal number of the municipality defined by the statistics office.
        """
        pass  # pragma: no cover
