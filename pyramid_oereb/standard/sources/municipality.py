# -*- coding: utf-8 -*-

from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.lib import b64
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.sources import BaseDatabaseSource
from geoalchemy2.shape import to_shape

from pyramid_oereb.lib.sources.municipality import MunicipalityBaseSource


class DatabaseSource(BaseDatabaseSource, MunicipalityBaseSource):

    def read(self, params):
        """
        Central method to read a municipality by it's id_bfs identifier.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                logo = ImageRecord(b64.decode(result.logo))
                self.records.append(self._record_class_(
                    result.fosnr,
                    result.name,
                    result.published,
                    logo,
                    geom=to_shape(result.geom).wkt if isinstance(
                        result.geom, _SpatialElement) else None,
                ))
        finally:
            session.close()
