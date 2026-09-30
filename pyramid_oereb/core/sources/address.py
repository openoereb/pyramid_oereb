# -*- coding: utf-8 -*-

from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.address import AddressRecord


class AddressBaseSource(Base):
    """
    Base class for address sources.
    """
    _record_class_ = AddressRecord

    def read(self, params, street_name: str, zip_code: int, street_number: str | None = None):
        """
        Every address source must implement a read method with the same signature.
        To integrate a custom address source, implement this method in your source class.

        The method reads addresses from the configured source matching the supplied criteria.

        Args:
            params (pyramid_oereb.core.views.webservice.Parameter):
                The parameters of the extract request
            street_name (str):
                The name of the street
            zip_code (int):
                The postal code
            street_number (str | None):
                The house or street number
        """
        pass  # pragma: no cover
