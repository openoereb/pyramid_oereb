# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver

from pyramid_oereb.core.records.address import AddressRecord
from pyramid_oereb.core.sources.address import AddressBaseSource


class AddressReader(object):
    """
    The central access point for reading addresses. It delegates all operations to a source
    implementation defined by a Python dotted import path. When this reader is instantiated,
    an instance of the defined source class is created as well, with all
    `**kwargs` passed to its constructor.

    The address is a combination of a street name, a zip code, and optionally a street number.
    """

    def __init__(self, dotted_source_class_path: str | AddressBaseSource, **params):
        """
        Args:
            dotted_source_class_path (str or pyramid_oereb.core.readers.address.AddressBaseSource):
                The path to the class representing the source used by this reader. The
                class must exist and implement the basic source behavior of the
                `pyramid_oereb.core.readers.address.AddressBaseSource`.
            params:
                kwrgs forwarded to the constructor of the configured source class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, params, street_name: str, zip_code: int, street_number: str | None = None) \
            -> list[AddressRecord]:
        """
        Reads addresses from the configured source matching the supplied criteria.

        The method delegates the lookup of the addresses to the configured source implementation.

        Note:
            Subclasses must implement this method with the same signature and return
            a list of `pyramid_oereb.core.records.address.AddressRecord` objects.
            Changing the signature or return type breaks the public API contract.

        Args:
            params (pyramid_oereb.core.views.webservice.Parameter):
                The parameters of the extract request
            street_name (str):
                The name of the street
            zip_code (int):
                The postal code
            street_number (str | None):
                The house or street number. If omitted, all addresses matching the street name
                and postal code are returned.

        Returns:
            list[pyramid_oereb.core.records.address.AddressRecord]:
                A list of address records matching the supplied search criteria.
        """
        return self._source_.read(params, street_name, zip_code, street_number)
