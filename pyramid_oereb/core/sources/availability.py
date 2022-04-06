# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.availability import AvailabilityRecord


class AvailabilityBaseSource(Base):
    """
    Base class for availability sources.

    Attributes:
        records (list of pyramid_oereb.core.records.availability.AvailabilityRecord): List
            of availability records.
    """
    _record_class_ = AvailabilityRecord

    def read(self):
        """
        Every availability source has to implement a read method. This method must accept no
        parameters. Because it should deliver all items available.
        If you want to adapt to your own source for availability, this is the point where to hook in.

        """
        pass  # pragma: no cover
