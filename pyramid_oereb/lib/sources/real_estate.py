# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from geoalchemy2.shape import to_shape


class RealEstateBaseSource(Base):
    _record_class_ = RealEstateRecord


class RealEstateDatabaseSource(BaseDatabaseSource, RealEstateBaseSource):

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
                to_shape(result.limit).wkt if isinstance(result.limit, _SpatialElement) else None,
                number=result.number,
                identdn=result.identdn,
                egrid=result.egrid
            ))
