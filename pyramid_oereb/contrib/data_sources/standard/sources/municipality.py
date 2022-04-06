# -*- coding: utf-8 -*-

from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.core.sources import BaseDatabaseSource
from geoalchemy2.shape import to_shape

from pyramid_oereb.core.sources.municipality import MunicipalityBaseSource


class DatabaseSource(BaseDatabaseSource, MunicipalityBaseSource):

    def read(self):
        """
        The read method to access the standard database structure. It uses SQL-Alchemy for querying. It does
        not accept any parameters nor it applies any filter on the database query. It simply loads all
        content from the configured model.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            self.records = list()
            results = session.query(self._model_).all()
            for result in results:
                self.records.append(self._record_class_(
                    result.fosnr,
                    result.name,
                    result.published,
                    geom=to_shape(result.geom).wkt if isinstance(
                        result.geom, _SpatialElement) else None,
                ))
        finally:
            session.close()
