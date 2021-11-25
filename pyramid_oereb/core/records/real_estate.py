# -*- coding: utf-8 -*-

class RealEstateRecord(object):
    """
    Basic characteristics and geometry of the property to be analysed.

    Attributes:
        plan_for_land_register (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service to
            be used for the land registry map.
        highlight (pyramid_oereb.lib.records.view_service.ViewServiceRecord): the view service with the wms
        image of the highlighted real estate.
        areas_ratio (decimal): Ratio of geometrical area and area from land registry.
    """

    plan_for_land_register = None
    plan_for_land_register_main_page = None
    highlight = None
    areas_ratio = 1.0

    def __init__(self, type, canton, municipality, fosnr, land_registry_area, limit,
                 metadata_of_geographical_base_data=None, number=None, identdn=None, egrid=None,
                 subunit_of_land_register=None, subunit_of_land_register_designation=None,
                 public_law_restrictions=None, references=None):
        """

        Args:
            type (unicode): The property type. This attribute will be translated with the configured
                corresponding value.
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
            subunit_of_land_register (unicode or None): Subunit of the land register if existing.
            subunit_of_land_register_designation (unicode or None): Dexciption of
                subunit_of_land_register if exisiting.
            public_law_restrictions (list of pyramid_oereb.lib.records.plr.PlrRecord or None): List of public
                law restrictions for this real estate
            references (list of pyramid_oereb.lib.records.documents.DocumentRecord or None): Documents
                associated with this real estate
            plan_for_land_register (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view
                service to be used for the land registry map
            plan_for_land_register_main_page (pyramid_oereb.lib.records.view_service.ViewServiceRecord):
                The view service to be used for the land registry map used on the main page
        """
        self.number = number
        self.identdn = identdn
        self.egrid = egrid
        self.type = type
        self.canton = canton
        self.municipality = municipality
        self.subunit_of_land_register = subunit_of_land_register
        self.subunit_of_land_register_designation = subunit_of_land_register_designation
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

    def set_main_page_view_service(self, plan_for_land_register_main_page):
        """
        Sets the view service to generate the land registry map for the real estate.

        Args:
            plan_for_land_register_main_page (pyramid_oereb.lib.records.view_service.ViewServiceRecord):
                The view service to be used for the land registry map used on the main page
        """
        self.plan_for_land_register_main_page = plan_for_land_register_main_page

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
