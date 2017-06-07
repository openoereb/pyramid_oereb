# -*- coding: utf-8 -*-

from pyramid.path import DottedNameResolver

from pyramid_oereb import Config
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


class RealEstateReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader accessor for real estates inside the application.

        Args:
            dotted_source_class_path (str): The path to the class which represents the source
                used by thisreader. This class must exist and it must implement basic source
                behaviour.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted namedefined class.
        """
        source_class = DottedNameResolver().resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, nb_ident=None, number=None, egrid=None, geometry=None):
        """
        The central read accessor method to get all desired records from configured source.

        Args:
            nb_ident (int or None): The identification number of the desired real estate. This
                parameter is directlyrelated to the number parameter and both must be set!
                Combination will deliver only one result orcrashes.
            number (str or None): The number of parcel or also known real estate. This parameter
                is directlyrelated to the nb_ident parameter and both must be set!
                Combination will deliver only one result orcrashes.
            (str or None): The unique identifier of the desired real estate. This will deliver
                only one result orcrashes.
            geometry (str): A geometry as WKT string which is used to obtain intersected real
                estates. This maydeliver several results.

        Returns:
            list of pyramid_oereb.lib.records.real_estate.RealEstateRecord: the list of all found
            records
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
