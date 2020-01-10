# -*- coding: utf-8 -*-

from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.lib import b64
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.sources import BaseDatabaseSource
from geoalchemy2.shape import to_shape

from pyramid_oereb.lib.sources.municipality import MunicipalityBaseSource


class DatabaseSource(BaseDatabaseSource, MunicipalityBaseSource):

    def read(self, params, fosnr=None):
        """
        Central method to read a municipality by it's id_bfs identifier.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            fosnr (int or None): The federal number of the municipality defined by the statistics office.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            self.records = list()
            if fosnr:
                results = session.query(self._model_).filter(self._model_.fosnr == fosnr).all()
            else:
                results = session.query(self._model_).all()
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
