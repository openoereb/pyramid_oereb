# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.municipality import MunicipalityRecord
from geoalchemy2.shape import to_shape


class MunicipalityBaseSource(Base):
    _record_class_ = MunicipalityRecord

    def read(self, id_bfs):
        pass


class MunicipalityDatabaseSource(BaseDatabaseSource, MunicipalityBaseSource):

    def read(self, id_bfs):
        """
        Central method to read a municipality by it's id_bfs identifier.
        :param id_bfs: The unique id_bfs for the desired municipality.
        :type id_bfs: int
        """
        session = self._adapter_.get_session(self._key_)
        query = session.query(self._model_)
        results = [query.filter(self._model_.id_bfs == id_bfs).one()]

        self.records = list()
        for result in results:
            self.records.append(self._record_class_(
                result.id_bfs,
                result.name,
                result.published,
                geom=to_shape(result.geom).wkt if isinstance(
                    result.geom, _SpatialElement) else None,
            ))
