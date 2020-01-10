# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.real_estate import RealEstateRecord


class RealEstateBaseSource(Base):
    """
    Base class for real estate sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.real_estate.RealEstateRecord): List of real estate records.
    """
    _record_class_ = RealEstateRecord

    def read(self, params, nb_ident=None, number=None, egrid=None, geometry=None):
        """
        Every real estate source has to implement a read method. This method must accept the four key word
        parameters. If you want adapt to your own source for real estates, this is the point where to hook in.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            nb_ident (int or None): The identification number of the desired real estate. This
                parameter is directly related to the number parameter and both must be set!
                Combination must deliver only one result or must raise an error.
            number (str or None): The number of parcel or also known real estate. This parameter
                is directly related to the nb_ident parameter and both must be set!
                Combination must deliver only one result or must raise an error.
            (str or None): The unique identifier of the desired real estate. This must deliver only one
                result or must raise an error.
            geometry (str): A geometry as WKT string which is used to obtain intersected real
                estates. This may deliver several results.
        """
        pass  # pragma: no cover
