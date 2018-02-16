# -*- coding: utf-8 -*-
from pyramid_oereb import Config
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.lib.url import add_url_params


class RealEstateRecord(object):
    """
    Basic characteristics and geometry of the property to be analysed.

    Attributes:
        plan_for_land_register (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service to
            be used for the land registry map.
        highlight (str): The url which produces a image with the highlighted real estate from a wms.
        areas_ratio (decimal): Ratio of geometrical area and area from land registry.
    """

    plan_for_land_register = None
    highlight = None
    areas_ratio = 1.0

    def __init__(self, type, canton, municipality, fosnr, land_registry_area, limit,
                 metadata_of_geographical_base_data=None, number=None, identdn=None, egrid=None,
                 subunit_of_land_register=None, public_law_restrictions=None, references=None):
        """

        Args:
            type (unicode): The property type
            canton (unicode): The abbreviation of the canton the property is located in
            municipality (unicode): The municipality the property is located in
            fosnr (int): The federal number of the municipality defined by the statistics office
            land_registry_area (int): Area of the property as defined in the land registry
            limit (shapely.geometry.MultiPolygon): The boundary of the property as geometry in as shapely
                multi polygon
            metadata_of_geographical_base_data (uri): Link to the metadata of the geodata
            number (unicode or None):  The official cantonal number of the property
            identdn (unicode or None): The unique identifier of the property
            egrid (unicode or None): The federal property identifier
            subunit_of_land_register (unicode or None): Subunit of the land register if existing
            public_law_restrictions (list of pyramid_oereb.lib.records.plr.PlrRecord or None): List of public
                law restrictions for this real estate
            references (list of pyramid_oereb.lib.records.documents.DocumentRecord or None): Documents
                associated with this real estate
            plan_for_land_register (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view
                service to be used for the land registry map
        """
        self.number = number
        self.identdn = identdn
        self.egrid = egrid
        self.type = type
        self.canton = canton
        self.municipality = municipality
        self.subunit_of_land_register = subunit_of_land_register
        self.fosnr = fosnr
        self.metadata_of_geographical_base_data = metadata_of_geographical_base_data
        self.land_registry_area = int(round(land_registry_area, 0))
        self.limit = limit
        if isinstance(public_law_restrictions, list):
            self.public_law_restrictions = public_law_restrictions
        else:
            self.public_law_restrictions = []
        if isinstance(references, list):
            self.references = references
        else:
            self.references = []
        self.areas_ratio = self.limit.area / self.land_registry_area

    def set_view_service(self, plan_for_land_register):
        """
        Sets the view service to generate the land registry map for the real estate.

        Args:
            plan_for_land_register (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view
                service to be used for the land registry map.
        """
        self.plan_for_land_register = plan_for_land_register

    def set_highlight_url(self, sld_url):
        configured_params = Config.get_real_estate_config().get('visualisation').get('url_params')
        additional_url_params = {}
        for param in configured_params:
            additional_url_params.update({param: getattr(self, param)})
        updated_sld_url = add_url_params(sld_url, additional_url_params)
        self.highlight = ViewServiceRecord(
            add_url_params(self.plan_for_land_register.reference_wms, {'sld': updated_sld_url}),
            ''
        )
        self.highlight.download_wms_content()

    def __str__(self):
        return '<%s -- number: %s identdn: %s egrid: %s type: %s' \
                    ' canton: %s municipality: %s subunit_of_land_register: %s fosnr: %s' \
                    ' metadata_of_geographical_base_data: %s land_registry_area: %s' \
                    ' limit: %s public_law_restrictions: %s references: %s' \
                    ' areas_ratio: %s>' % (
                        self.__class__.__name__,
                        self.number, self.identdn, self.egrid, self.type,
                        self.canton, self.municipality, self.subunit_of_land_register, self.fosnr,
                        self.metadata_of_geographical_base_data, self.land_registry_area,
                        self.limit, self.public_law_restrictions, self.references,
                        self.areas_ratio)
