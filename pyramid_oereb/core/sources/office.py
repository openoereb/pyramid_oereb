# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.office import OfficeRecord


class OfficeBaseSource(Base):
    """
    Base class for office sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.office.OfficeRecord): List of office records.
    """
    _record_class_ = OfficeRecord

    def read(self):
        """
        Every office source has to implement a read method. This method must accept no parameters. Because
        it should deliver all items available.
        If you want adapt to your own source for offices, this is the point where to hook in.
        """
        pass  # pragma: no cover
