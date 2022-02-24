# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.general_information import GeneralInformationRecord


class GeneralInformationBaseSource(Base):
    """
    Base class for GeneralInformation values source.

    Attributes:
        records (list of pyramid_oereb.lib.records.general_information.GeneralInformationRecord): List of
        general information records.
    """
    _record_class_ = GeneralInformationRecord

    def read(self):
        """
        Every general information source has to implement a read method.
        This method must accept no parameters. Because it should deliver all items available.
        If you want adapt to your own source for general information labels, this is the point
        where to hook in.
        """
        pass  # pragma: no cover
