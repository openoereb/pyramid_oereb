# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Query, Session
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.core.records.address import AddressRecord
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.address import AddressBaseSource
from pyramid_oereb.core.views.webservice import Parameter


class DatabaseSource(BaseDatabaseSource, AddressBaseSource):

    def read(self, params: Parameter, street_name: str, zip_code: int, street_number: str | None = None) \
            -> list[AddressRecord]:
        """
        The read method for accessing the standard database schema.
        It uses SQLAlchemy to query the database for records matching the supplied arguments.

        Args:
            params (pyramid_oereb.core.views.webservice.Parameter):
                The parameters of the extract request
            street_name (str):
                The name of the street
            zip_code (int):
                The postal code
            street_number (str | None):
                The house or street number

        Returns:
            list[pyramid_oereb.core.records.address.AddressRecord]:
                A list of address records matching the supplied search criteria.
        """
        session: Session = self._adapter_.get_session(self._key_)
        try:
            query: Query = session.query(self._model_)
            query = query.filter(
                self._model_.street_name == street_name
            ).filter(
                self._model_.zip_code == zip_code
            )

            if street_number is not None:
                query = query.filter(self._model_.street_number == street_number)

            results: list = query.all()

            records: list[AddressRecord] = []
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
