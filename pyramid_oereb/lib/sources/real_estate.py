# -*- coding: utf-8 -*-
from geoalchemy2 import WKTElement
from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from geoalchemy2.shape import to_shape


class RealEstateDatabaseSource(BaseDatabaseSource):

    def __init__(self, **kwargs):
        """
        The plug for real estates which uses a database as source.
        :param key: The key for the database connection which should be used from the database adapter,
        passed to this instance.
        :type key: str
        :param adapter: The database adapter which provides access to the desired database session
        :type adapter: pyramid_oereb.lib.adapter.DatabaseAdapter
        :param model: The orm to map database source to plr style
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        """
        if kwargs.get('db_connection'):
            key = kwargs.get('db_connection')
        else:
            raise ConfigurationError('"db_connection" for source has to be defined in used yaml '
                                     'configuration file')
        if kwargs.get('model'):
            model = DottedNameResolver().resolve(kwargs.get('model'))
        else:
            raise ConfigurationError('"model" for source has to be defined in used yaml configuration file')

        super(RealEstateDatabaseSource, self).__init__(key, model, RealEstateRecord)

    def read(self, **kwargs):
        """
        Central method to read all plrs.
        :param kwargs: Arbitrary keyword arguments. It must contain the keys 'nb_ident' and 'number' or the
        single key 'egrid' as string.
        """
        session = self._adapter_.get_session(self._key_)
        query = session.query(self._model_)
        if kwargs.get('nb_ident') and kwargs.get('number'):
            results = [query.filter(
                self._model_.number == kwargs.get('number')
            ).filter(
                self._model_.identdn == kwargs.get('nb_ident')
            ).one()]
        elif kwargs.get('egrid'):
            results = [query.filter(self._model_.egrid == kwargs.get('egrid')).one()]
        elif kwargs.get('geometry'):
            results = query.filter(self._model_.limit.ST_Intersects(kwargs.get('geometry'))).all()
        else:
            raise AttributeError('Necessary parameter were missing.')

        self.records = list()
        for result in results:
            self.records.append(self._record_class_(
                result.type,
                result.canton,
                result.municipality,
                result.fosnr,
                result.metadata_of_geographical_base_data,
                result.land_registry_area,
                to_shape(result.limit).wkt if isinstance(result.limit, WKTElement) else None,
                number=result.number,
                identdn=result.identdn,
                egrid=result.egrid
            ))
