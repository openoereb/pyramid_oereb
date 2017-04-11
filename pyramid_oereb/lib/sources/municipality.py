# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.municipality import MunicipalityRecord
from geoalchemy2.shape import to_shape


class MunicipalityBaseSource(Base):
    _record_class_ = MunicipalityRecord

    def read(self):
        pass  # pragma: no cover


class MunicipalityDatabaseSource(BaseDatabaseSource, MunicipalityBaseSource):

    def read(self):
        """
        Central method to read a municipality by it's id_bfs identifier.
        """
        session = self._adapter_.get_session(self._key_)
        results = session.query(self._model_).all()

        self.records = list()
        for result in results:
            self.records.append(self._record_class_(
                result.fosnr,
                result.name,
                result.published,
                geom=to_shape(result.geom).wkt if isinstance(
                    result.geom, _SpatialElement) else None,
            ))
