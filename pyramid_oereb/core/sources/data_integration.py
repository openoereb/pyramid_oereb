# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.data_integration import DataIntegrationRecord


class DataIntegrationBaseSource(Base):
    """
    Base class for data integration sources.

    Attributes:
        records (list of pyramid_oereb.core.records.data_integration.DataIntegrationRecord): List
            of availability records.
    """
    _record_class_ = DataIntegrationRecord

    def read(self):
        """
        Every availability source has to implement a read method. This method must accept no
        parameters. Because it should deliver all items available.
        If you want to adapt to your own source for data integration, this is the point where
        to hook in.

        """
        pass  # pragma: no cover
