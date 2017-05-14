# -*- coding: utf-8 -*-
import logging
from sqlalchemy.orm.exc import NoResultFound
from pyramid_oereb.lib.records.plr import PlrRecord

log = logging.getLogger('pyramid_oereb')


class Processor(object):

    def __init__(self, real_estate_reader, municipality_reader, plr_sources, extract_reader,
                 min_area=1.0, min_length=1.0, point_types=['Point', 'MultiPoint'],
                 line_types=['LineString', 'LinearRing', 'MultiLineString'],
                 polygon_types=['Polygon', 'MultiPolygon']):
        """
        The Processor class is directly bound to the get_extract_by_id service in this application. It's task
        is to unsnarl the difficult model of the oereb extract and handle all objects inside this extract
        correctly. In addition it provides an easy to use method interface to access the information.
        It is also used to wrap all accessors in one point to have a processing interface.

        :var real_estate_reader: The real estate reader instance for runtime use.
        :vartype real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        :var municipality_reader: The municipality reader instance for runtime use.
        :vartype municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        :var plr_sources: The public law restriction source instances for runtime use wrapped in a list.
        :vartype plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        :var extract_reader: The extract reader instance for runtime use.
        :vartype extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        :var point_types: The different point geometry types a restriction could be defined in
        :vartype point_types: list of str
        :var line_types: The different line geometry types a restriction could take
        :vartype line_types: list of str
        :var polygon_types: The different point geometry types a restriction could have
        :vartype polygon_types: list of str
        :var min_area: The minimal area for a public law restriction to be displayed in the cadastre
        :vartype min_area: decimal
        :var min_length: The minimal length for a public law restriction to be displayed in the cadastre
        :vartype min_length: decimal
        """
        self._real_estate_reader_ = real_estate_reader
        self._municipality_reader_ = municipality_reader
        self._plr_sources_ = plr_sources
        self._extract_reader_ = extract_reader
        self._min_area_ = min_area
        self._min_length_ = min_length
        self.point_types = point_types
        self.line_types = line_types
        self.polygon_types = polygon_types

    def plr_tolerance_check(self, extract):
        """
        The function checking if the found plr results exceed the minimal surface or length
        value defined in the configuration and should therefor be represented in the extract
        or considered 'false trues' and be removed from the results.

        :var extract: The extract in it's unvalidated form
        :vartype extract: pyramid_oereb.lib.records.extract.ExtractRecord
        :return: Returns the updated extract
        :rtype: pyramid_oereb.lib.records.extract.ExtractRecord
        """
        real_estate = extract.real_estate
        real_estate_feature_area = extract.real_estate.limit.area
        land_registry_area = extract.real_estate.land_registry_area
        areas_ratio = real_estate_feature_area/land_registry_area
        geom_cleaner = []
        plr_cleaner = []

        for index, public_law_restriction in enumerate(extract.real_estate.public_law_restrictions):
            if isinstance(public_law_restriction, PlrRecord):
                for geometry in public_law_restriction.geometries:
                    geometryType = geometry.geom_type
                    if geometryType in self.point_types:
                        pass
                    elif geometryType in self.line_types:
                        extract.real_estate.public_law_restrictions[index].length = geometry.length
                        if extract.real_estate.public_law_restrictions[index].length < self._min_length_:
                            geom_cleaner.append(geometry)
                        else:
                            extract.real_estate.public_law_restrictions[index].units = 'm'
                    elif geometryType in self.polygon_types:
                        # Compensation of the difference between technical area from land registry and the
                        # calculated area of the geometry
                        compensated_area = geometry.area*areas_ratio
                        extract.real_estate.public_law_restrictions[index].area = compensated_area
                        if extract.real_estate.public_law_restrictions[index].area < self._min_area_:
                            geom_cleaner.append(geometry)
                        else:
                            extract.real_estate.public_law_restrictions[index].part_in_percent = \
                                round(((compensated_area/real_estate.limit.area)*100), 1)
                            extract.real_estate.public_law_restrictions[index].units = 'm2'
                    else:
                        msg = 'Error: unknown geometry type "{type}"'.format(type=geometryType)
                        log.error(msg)
                        raise LookupError(msg)
                # Remove small geometry from geometries list
                for geom in geom_cleaner:
                    extract.real_estate.public_law_restrictions[index].geometries.remove(geom)
                # Test if the geometries list is now empty - if so remove plr from plr list
                if len(extract.real_estate.public_law_restrictions[index].geometries) == 0:
                    plr_cleaner.append(index)

        for j in reversed(plr_cleaner):
            extract.real_estate.public_law_restrictions.pop(j)

        return extract

    @property
    def real_estate_reader(self):
        """

        :return: The real estate reader instance.
        :rtype real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        """
        return self._real_estate_reader_

    @property
    def municipality_reader(self):
        """

        :return: The municipality reader reader instance.
        :rtype municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        """
        return self._municipality_reader_

    @property
    def plr_sources(self):
        """

        :return: The list of plr source instances.
        :rtype plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        """
        return self._plr_sources_

    @property
    def extract_reader(self):
        """

        :return: The extract reader instance.
        :rtype extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        """
        return self._extract_reader_

    def process(self, real_estate):
        """
        Central processing method to hook in from webservice.

        :var real_estate: The real estate reader to obtain the real estates record.
        :vartype real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :return:
        """
        municipalities = self._municipality_reader_.read()
        for municipality in municipalities:
            if municipality.fosnr == real_estate.fosnr:
                if not municipality.published:
                    msg = 'Main switch decides to block requested extract because municipality ' \
                          '"{id}", ""{name} has set a negative published switch.'.format(
                                id=municipality.fosnr, name=municipality.name
                            )
                    log.error(msg)
                    raise NotImplementedError(msg)
                extract_raw = self._extract_reader_.read(real_estate, municipality.logo)
                extract = self.plr_tolerance_check(extract_raw)
                return extract.to_extract()
        msg = 'There was a problem with your provided municipality data. Municipality could not be ' \
              'found in the provided set: "{id}"'.format(
                    id=real_estate.fosnr
                )
        log.error(msg)
        raise LookupError(msg)
