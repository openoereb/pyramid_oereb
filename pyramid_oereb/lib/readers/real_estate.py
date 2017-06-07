# -*- coding: utf-8 -*-

from pyramid.path import DottedNameResolver

from pyramid_oereb import Config
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


class RealEstateReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader accessor for real estates inside the application.
        :param dotted_source_class_path: The path to the class which represents the source used by this
        reader. This class must exist and it must implement basic source behaviour.
        :type dotted_source_class_path: str
        :param params: kwargs, which are necessary as configuration parameter for the above by dotted name
        defined class.
        :type: kwargs
        """
        source_class = DottedNameResolver().resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, nb_ident=None, number=None, egrid=None, geometry=None):
        """
        The central read accessor method to get all desired records from configured source.

        :param nb_ident: The identification number of the desired real estate. This parameter is directly
        related to the number parameter and both must be set! Combination will deliver only one result or
        crashes.
        :type nb_ident: int or None
        :param number: The number of parcel or also known real estate. This parameter is directly
        related to the nb_ident parameter and both must be set! Combination will deliver only one result or
        crashes.
        :type number: str or None
        :param egrid: The unique identifier of the desired real estate. This will deliver only one result or
        crashes.
        :type: str or None
        :param geometry: A geometry as WKT string which is used to obtain intersected real estates. This may
        deliver several results.
        :type geometry: str
        :return: the list of all found records
        :rtype: list of pyramid_oereb.lib.records.real_estate.RealEstateRecord
        """
        real_estate_view_service = ViewServiceRecord(
            link_wms=Config.get_real_estate_config().get('view_service').get('reference_wms'),
            legend_web=Config.get_real_estate_config().get('view_service').get('legend_at_web')
        )
        self._source_.read(nb_ident=nb_ident, number=number, egrid=egrid, geometry=geometry)
        for r in self._source_.records:
            if isinstance(r, RealEstateRecord):
                r.set_view_service(real_estate_view_service)
        return self._source_.records
