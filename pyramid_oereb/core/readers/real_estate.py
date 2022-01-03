# -*- coding: utf-8 -*-

from pyramid.path import DottedNameResolver

from pyramid_oereb import Config
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord


class RealEstateReader(object):
    """
    The central reader for real estates. It is directly bound to a so called source
    which is defined by a pythonic dotted string to the class definition of this source.
    An instance of the passed source will be created on instantiation of this reader class by passing through
    the parameter kwargs.
    """

    def __init__(self, dotted_source_class_path, **params):
        """
        Args:
            dotted_source_class_path (str or pyramid_oereb.lib.sources.real_estate.RealEstateBaseSource): The
                path to the class which represents the source used by this reader. This class must exist and
                it must implement basic source behaviour of the
                :ref:`api-pyramid_oereb-core-sources-real_estate-realestatebasesource`.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted name defined class.
        """
        source_class = DottedNameResolver().resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, params, nb_ident=None, number=None, egrid=None, geometry=None):
        """
        The central read accessor method to get all desired records from configured source.

        .. note:: If you subclass this class your implementation needs to offer this method in the same
            signature. Means the parameters must be the same and the return must be a list of
            :ref:`api-pyramid_oereb-core-records-real_estate-realestaterecord`. Otherwise the API like way the
            server works would be broken.

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
            geometry (str): A geometry as WKT string which is used to obtain intersected real
                estates. This may deliver several results.

        Returns:
            list of pyramid_oereb.core.records.real_estate.RealEstateRecord:
                The list of all found records filtered by the passed criteria.
        """
        plan_for_land_register_config = Config.get_plan_for_land_register_config()

        real_estate_view_service = ViewServiceRecord(
            plan_for_land_register_config.get('reference_wms'),
            plan_for_land_register_config.get('layer_index'),
            plan_for_land_register_config.get('layer_opacity'),
            Config.get('default_language'),
            Config.get('srid'),
            Config.get('proxies')
        )

        plan_for_land_register_main_page_config = Config.get_plan_for_land_register_main_page_config()
        real_estate_main_page_view_service = ViewServiceRecord(
            plan_for_land_register_main_page_config.get('reference_wms'),
            plan_for_land_register_main_page_config.get('layer_index'),
            plan_for_land_register_main_page_config.get('layer_opacity'),
            Config.get('default_language'),
            Config.get('srid'),
            Config.get('proxies')
        )

        self._source_.read(params, nb_ident=nb_ident, number=number, egrid=egrid, geometry=geometry)
        for r in self._source_.records:
            if isinstance(r, RealEstateRecord):
                r.set_view_service(real_estate_view_service)
                r.set_main_page_view_service(real_estate_main_page_view_service)
        return self._source_.records
