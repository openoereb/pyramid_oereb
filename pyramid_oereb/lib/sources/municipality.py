# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.municipality import MunicipalityRecord
from geoalchemy2.shape import to_shape


class MunicipalityBaseSource(Base):
    _record_class_ = MunicipalityRecord


class MunicipalityDatabaseSource(BaseDatabaseSource, MunicipalityBaseSource):

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
            self.records.append(self._record_class_(
                result.id_bfs,
                result.name,
                result.published,
                geom=to_shape(result.geom).wkt if isinstance(
                    result.geom, _SpatialElement) else None,
            ))
