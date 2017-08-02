# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord


class ExclusionOfLiabilityBaseSource(Base):
    """
    Base class for exclusion of liability sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.exclusion_of_liability.ExclusionOfLiabilityRecord): List
            of exclusion of liability records.
    """
    _record_class_ = ExclusionOfLiabilityRecord

    def read(self):
        """
        Every exclusion of liability source has to implement a read method. This method must accept no
        parameters. Because it should deliver all items available.
        If you want adapt to your own source for exclusion of liabilities, this is the point where to hook in.
        """
        pass  # pragma: no cover
