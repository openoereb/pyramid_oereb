# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.theme import ThemeRecord


class ThemeBaseSource(Base):
    """
    Base class for theme sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.theme.ThemeRecord): List of theme records.
    """
    _record_class_ = ThemeRecord

    def read(self):
        """
        Every theme source has to implement a read method. This method must accept no parameters. Because
        it should deliver all items available.
        If you want adapt to your own source for themes, this is the point where to hook in.
        """
        pass  # pragma: no cover
