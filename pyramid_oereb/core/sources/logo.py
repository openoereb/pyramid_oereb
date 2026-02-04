# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.logo import LogoRecord


class LogoBaseSource(Base):
    """
    Base class for logo images source.

    Attributes:
        records (list of pyramid_oereb.lib.records.logo.LogoRecord): List of logos
        type records.
    """
    _record_class_ = LogoRecord

    def read(self):
        """
        Every logo source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for logo images, this is the point where to hook in.
        """
        pass  # pragma: no cover
