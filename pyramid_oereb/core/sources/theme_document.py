# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.theme_document import ThemeDocumentRecord


class ThemeDocumentBaseSource(Base):
    """
    Base class for theme document sources.

    Attributes:
        records (list of pyramid_oereb.core.records.theme.ThemeDocumentRecord): List of theme
            document records.
    """
    _record_class_ = ThemeDocumentRecord

    def read(self):
        """
        Every theme document source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for theme documents, this is the point where to hook in.
        """
        pass  # pragma: no cover
