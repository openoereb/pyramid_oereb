# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.real_estate_type import RealEstateTypeRecord


class RealEstateTypeBaseSource(Base):
    """
    Base class for real estate type values source.
    Attributes:
        records (list of pyramid_oereb.lib.records.real_estate_type.RealEstateTypeRecord): List of real estate
        type records.
    """
    _record_class_ = RealEstateTypeRecord

    def read(self, params=None):
        """
        Every real estate type source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for real estate type labels, this is the point where to hook in.
        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        pass  # pragma: no cover
