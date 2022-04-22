# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord


class DisclaimerBaseSource(Base):
    """
    Base class for exclusion of liability sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.disclaimer.DisclaimerRecord): List
            of exclusion of liability records.
    """
    _record_class_ = DisclaimerRecord

    def read(self):
        """
        Every disclaimer source has to implement a read method. This method must accept no
        parameters. Because it should deliver all items available.
        If you want adapt to your own source for disclaimer, this is the point where to hook in.
        """
        pass  # pragma: no cover
