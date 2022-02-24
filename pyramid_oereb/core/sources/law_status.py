# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.law_status import LawStatusRecord


class LawStatusBaseSource(Base):
    """
    Base class for law status values source.
    Attributes:
        records (list of pyramid_oereb.lib.records.law_status.LawStatusRecord): List of law status
        records.
    """
    _record_class_ = LawStatusRecord

    def read(self, params=None):
        """
        Every law status source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for real estate type labels, this is the point where to hook in.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        pass  # pragma: no cover
