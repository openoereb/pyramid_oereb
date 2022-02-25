# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement

from pyramid_oereb.core.sources import BaseDatabaseSource
from geoalchemy2.shape import to_shape

from pyramid_oereb.core.sources.real_estate import RealEstateBaseSource


class DatabaseSource(BaseDatabaseSource, RealEstateBaseSource):

    def read(self, params, nb_ident=None, number=None, egrid=None, geometry=None):
        """
        Central method to read all plrs (geometry input) or explicitly one plr (nb_ident+number/egrid input).

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            nb_ident (int or None): The identification number of the desired real estate. This
                parameter is directly related to the number parameter and both must be set!
                Combination will deliver only one result or crashes.
            number (str or None): The number of parcel or also known real estate. This parameter
                is directly related to the nb_ident parameter and both must be set!
                Combination will deliver only one result or crashes.
            (str or None): The unique identifier of the desired real estate. This will deliver
                only one result or crashes.
            geometry (str or None): A geometry as WKT string which is used to obtain intersected real
                estates. This may deliver several results.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            query = session.query(self._model_)
            if nb_ident and number:
                results = query.filter(self._model_.number == number, self._model_.identdn == nb_ident).all()
            elif egrid:
                results = query.filter(self._model_.egrid == egrid).all()
            elif geometry:
                results = query.filter(self._model_.limit.ST_Intersects(geometry)).all()
            else:
                raise AttributeError('Necessary parameter were missing.')

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.type,
                    result.canton,
                    result.municipality,
                    result.fosnr,
                    result.land_registry_area,
                    to_shape(result.limit) if isinstance(result.limit, _SpatialElement) else None,
                    metadata_of_geographical_base_data=result.metadata_of_geographical_base_data,
                    number=result.number,
                    identdn=result.identdn,
                    egrid=result.egrid,
                    subunit_of_land_register=result.subunit_of_land_register,
                    subunit_of_land_register_designation=result.subunit_of_land_register_designation
                ))

        finally:
            session.close()
