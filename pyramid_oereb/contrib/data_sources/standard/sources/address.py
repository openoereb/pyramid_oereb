# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.address import AddressBaseSource


class DatabaseSource(BaseDatabaseSource, AddressBaseSource):

    def read(self, params, street_name, zip_code, street_number):
        """
        The read method to access the standard database structure. It uses SQL-Alchemy for querying. It tries
        to find the items via passed arguments.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            street_name (unicode): The name of the street for the desired address.
            zip_code (int): The postal zipcode for the desired address.
            street_number (str): The house or so called street number of the desired address.

        Returns:
            list of pyramid_oereb.core.records.address.AddressRecord: The list of address records.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            query = session.query(self._model_)
            results = [query.filter(
                self._model_.street_name == street_name
            ).filter(
                self._model_.zip_code == zip_code
            ).filter(
                self._model_.street_number == street_number
            ).one()]

            records = []
            for result in results:
                records.append(self._record_class_(
                    result.street_name,
                    result.zip_code,
                    result.street_number,
                    to_shape(result.geom) if isinstance(result.geom, _SpatialElement) else None
                ))
            return records

        except NoResultFound:
            return []

        finally:
            session.close()
