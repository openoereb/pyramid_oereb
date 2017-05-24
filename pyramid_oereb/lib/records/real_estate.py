# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


class RealEstateRecord(object):

    def __init__(self, type, canton, municipality, fosnr, land_registry_area, limit,
                 metadata_of_geographical_base_data=None, number=None, identdn=None, egrid=None,
                 subunit_of_land_register=None, public_law_restrictions=None, references=None):
        """
        Basic caracteristics and geometry of the property to be analysed.
        :param type: The property type
        :type type: str
        :param canton: The abbreviation of the canton the property is located in
        :type canton: str
        :param municipality: The municipality the property is located in
        :type municipality: str
        :param fosnr: The federal number of the municipality defined by the statistics office
        :type fosnr: integer
        :param land_registry_area: Area of the property as defined in the land registry
        :type land_registry_area: integer
        :param limit: The boundary of the property as geometry in as shapely multi polygon
        :type limit: shapely.geometry.MultiPolygon
        :param metadata_of_geographical_base_data: Link to the metadata of the geodata
        :type metadata_of_geographical_base_data: uri
        :param number:  The official cantonal number of the property
        :type  number: str or None
        :param identdn: The unique identifier of the property
        :type  identdn: str or None
        :param egrid: The federal property identifier
        :type egrid: str or None
        :param subunit_of_land_register: Subunit of the land register if existing
        :type subunit_of_land_register: str or None
        :param public_law_restrictions: List of public law restrictions for this real estate
        :type public_law_restrictions: list of pyramid_oereb.lib.records.plr.PlrRecord or None
        :param references: Documents associated with this real estate
        :type references: list of pyramid_oereb.lib.records.documents.DocumentRecord or None
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
        :return:    List of available field names.
        :rtype:     list
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
        :return: Dictionary with values for the extract.
        :rtype: dict
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
