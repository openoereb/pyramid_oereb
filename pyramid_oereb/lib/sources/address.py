# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from geoalchemy2.shape import to_shape

from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.address import AddressRecord


class AddressBaseSource(Base):
    _record_class_ = AddressRecord


class AddressDatabaseSource(BaseDatabaseSource, AddressBaseSource):

    def read(self, **kwargs):
        """
        Central method to read one address.
        :param kwargs: Arbitrary keyword arguments. It must contain the keys 'street_name', 'zip_code' and
        'street_number'.
        """
        session = self._adapter_.get_session(self._key_)
        query = session.query(self._model_)
        if kwargs.get('street_name') and kwargs.get('zip_code') and kwargs.get('street_number'):
            results = [query.filter(
                self._model_.street_name == kwargs.get('street_name')
            ).filter(
                self._model_.zip_code == kwargs.get('zip_code')
            ).filter(
                self._model_.street_number == kwargs.get('street_number')
            ).one()]
        else:
            raise AttributeError('Necessary parameter were missing.')

        self.records = list()
        for result in results:
            self.records.append(self._record_class_(
                result.street_name,
                result.zip_code,
                result.street_number,
                to_shape(result.geom).wkt if isinstance(result.geom, _SpatialElement) else None
            ))
