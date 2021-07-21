# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.general_information import GeneralInformationRecord


class GeneralInformationBaseSource(Base):
    """
    Base class for GeneralInformation values source.

    Attributes:
        records (list of pyramid_oereb.lib.records.document_types.GeneralInformationRecord): List of general
        information records.
    """
    _record_class_ = GeneralInformationRecord

    def read(self):
        """
        Every general information source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for general information labels, this is the point where to hook in.
        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        pass  # pragma: no cover