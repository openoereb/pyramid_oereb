# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from geoalchemy2.shape import to_shape


class RealEstateDatabaseSource(BaseDatabaseSource):

    def __init__(self, key, adapter, model):
        """
        The plug for properties which uses a database as source.
        :param key: The key for the database connection which should be used from the database adapter,
        passed to this instance.
        :type key: str
        :param adapter: The database adapter which provides access to the desired database session
        :type adapter: pyramid_oereb.lib.adapter.DatabaseAdapter
        :param model: The orm to map database source to plr style
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        """
        super(RealEstateDatabaseSource, self).__init__(key, adapter, model, RealEstateRecord)

    def read(self, **kwargs):
        """
        Central method to read all plrs.
        :param kwargs: Arbitrary keyword arguments. It must contain the keys 'nb_ident' and 'number' or the
        single key 'egrid' as string.
        """
        session = self._adapter_.get_session(self._key_)
        query = session.query(self._model_)
        if kwargs.get('nb_ident') and kwargs.get('number'):
            result = query.filter(
                self._model_.nummer == kwargs.get('number')
            ).filter(
                self._model_.nbident == kwargs.get('nb_ident')
            ).one()
        else:
            result = query.filter(self._model_.egris_egrid == kwargs.get('egrid')).one()

        self.records = list()
        self.records.append(self._record_class_(
            result.type,
            result.canton,
            result.municipality,
            result.fosnr,
            result.metadata_of_geographical_base_data,
            result.land_regestry_area,
            to_shape(result.limit).wkt,
            number=result.number,
            identdn=result.identdn,
            egrid=result.egrid
        ))
