# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.records.municipality import MunicipalityRecord
from geoalchemy2.shape import to_shape


class MunicipalityDatabaseSource(BaseDatabaseSource):

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

        super(MunicipalityDatabaseSource, self).__init__(key, model)

    def read(self, **kwargs):
        """
        Central method to read a municipality by it's id_bfs identifier.
        :param kwargs: Arbitrary keyword arguments. It must contain the key 'id_bfs'.
        """
        session = self._adapter_.get_session(self._key_)
        query = session.query(self._model_)
        if kwargs.get('id_bfs'):
            results = [query.filter(
                self._model_.id_bfs == kwargs.get('id_bfs')
            ).one()]
        else:
            raise AttributeError('Necessary parameter were missing.')

        self.records = list()
        for result in results:
            self.records.append(MunicipalityRecord(
                result.id_bfs,
                result.name,
                result.published,
                geom=to_shape(result.geom).wkt if isinstance(
                    result.geom, _SpatialElement) else None,
            ))
