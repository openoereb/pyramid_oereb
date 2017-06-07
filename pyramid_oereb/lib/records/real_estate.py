# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


class RealEstateRecord(object):

    def __init__(self, type, canton, municipality, fosnr, land_registry_area, limit,
                 metadata_of_geographical_base_data=None, number=None, identdn=None, egrid=None,
                 subunit_of_land_register=None, public_law_restrictions=None, references=None):
        """
        Basic caracteristics and geometry of the property to be analysed.

        Args:
            type (str): The property type
            canton (str): The abbreviation of the canton the property is located in
            municipality (str): The municipality the property is located in
            fosnr (integer): The federal number of the municipality defined by the statistics
                office
            land_registry_area (integer): Area of the property as defined in the land registry
            limit (shapely.geometry.MultiPolygon): The boundary of the property as geometry in
                as shapely multi polygon
            metadata_of_geographical_base_data (uri): Link to the metadata of the geodata
            number (strorNone):  The official cantonal number of the property
            identdn (strorNone): The unique identifier of the property
            egrid (strorNone): The federal property identifier
            subunit_of_land_register (strorNone): Subunit of the land register if existing
            public_law_restrictions (listofpyramid_oereb.lib.records.plr.PlrRecordorNone): List
                of public law restrictions for this real estate
            references (listofpyramid_oereb.lib.records.documents.DocumentRecordorNone):
                Documents associated with this real estate
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
        self.land_registry_area = land_registry_area
        self.limit = limit
        # TODO: read the urls from configuration of the real estate. They are already defined there. This will
        # solve issue https://jira.camptocamp.com/browse/GSOREB-194
        self.plan_for_land_register = ViewServiceRecord(
            'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&'
            'SRS=EPSG:21781&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png&'
            'LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
            'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.1.1&'
            'FORMAT=image/png&LAYER=ch.bav.kataster-belasteter-standorte-oev.oereb'
        )
        if isinstance(public_law_restrictions, list):
            self.public_law_restrictions = public_law_restrictions
        else:
            self.public_law_restrictions = []
        if isinstance(references, list):
            self.references = references
        else:
            self.references = []
        self.areas_ratio = self.limit.area / self.land_registry_area

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            list:List of available field names.
        """
        return [
            'type',
            'canton',
            'municipality',
            'fosnr',
            'metadata_of_geographical_base_data',
            'land_registry_area',
            'limit',
            'number',
            'identdn',
            'egrid',
            'subunit_of_land_register',
            'plan_for_land_register',
            'public_law_restrictions',
            'references'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        Returns:
            dict: Dictionary with values for the extract.
        """
        extract = dict()
        for key in [
            'type',
            'canton',
            'municipality',
            'fosnr',
            'metadata_of_geographical_base_data',
            'land_registry_area',
            'number',
            'identdn',
            'egrid',
            'subunit_of_land_register'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value
        key = 'plan_for_land_register'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract()
        for key in [
            'public_law_restrictions',
            'references'
        ]:
            records = getattr(self, key)
            if records and len(records) > 0:
                extract[key] = [r.to_extract() for r in records]
        key = 'limit'
        extract[key] = str(getattr(self, key))

        return extract
