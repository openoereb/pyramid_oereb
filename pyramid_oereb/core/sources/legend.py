# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.view_service import LegendEntryRecord


class LegendBaseSource(Base):
    """
    Base class for exclusion of liability sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.view_service.LegendEntryRecord): List of legend entry
            records.
    """
    _record_class_ = LegendEntryRecord

    def read(self, params, **kwargs):
        """
        Every legend entry source has to implement a read method. If you want adapt to your own source for
        legend entries, this is the point where to hook in.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            (kwargs): Arbitrary keyword arguments.
        """
        pass  # pragma: no cover
