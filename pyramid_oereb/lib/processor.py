# -*- coding: utf-8 -*-
from sqlalchemy.orm.exc import NoResultFound
from pyramid_oereb.lib.records.plr import PlrRecord


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

        :param real_estate_reader: The real estate reader instance for runtime use.
        :type real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        :param municipality_reader: The municipality reader instance for runtime use.
        :type municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        :param plr_sources: The public law restriction source instances for runtime use wrapped in a list.
        :type plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        :param extract_reader: The extract reader instance for runtime use.
        :type extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        :param point_types: The different point geometry types a restriction could be defined in
        :type point_types: list of str
        :param line_types: The different line geometry types a restriction could take
        :type line_types: list of str
        :param polygon_types: The different point geometry types a restriction could have
        :type polygon_types: list of str
        :param min_area: The minimal area for a public law restriction to be displayed in the cadastre
        :type min_area: decimal
        :param min_length: The minimal length for a public law restriction to be displayed in the cadastre
        :type min_length: decimal
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

        :param extract: The extract in it's unvalidated form
        :type extract: pyramid_oereb.lib.records.extract.ExtractRecord
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
                        results = geometry.geom.intersection(real_estate.limit)
                        element_count = len(results)
                        for element in results:
                            if element.length < self._min_length_:
                                element_count -= 1
                            else:
                                extract.real_estate.public_law_restrictions[index].length += element.length
                                extract.real_estate.public_law_restrictions[index].units = 'm'
                            if element_count == 0:
                                geom_cleaner.append(geometry)
                    elif geometryType in self.polygon_types:
                        results = geometry.geom.intersection(real_estate.limit)
                        element_count = len(results)
                        # Compensation of the difference between technical area from land registry and the
                        # calculated area of the geometry
                        for element in results:
                            compensated_area = element.area*areas_ratio
                            if compensated_area < self._min_area_:
                                element_count -= 1
                            else:
                                extract.real_estate.public_law_restrictions[index].area += compensated_area
                                extract.real_estate.public_law_restrictions[index].part_in_percent = \
                                    round(((extract.real_estate.public_law_restrictions[index].area /
                                            real_estate.limit.area)*100), 1)
                                extract.real_estate.public_law_restrictions[index].units = 'm2'
                            if element_count == 0:
                                geom_cleaner.append(geometry)
                    else:
                        # TODO: configure a proper error message
                        print 'Error: unknown geometry type'
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

        :param real_estate: The real estate reader to obtain the real estates record.
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :return:
        """
        municipalities = self._municipality_reader_.read()
        for municipality in municipalities:
            if municipality.fosnr == real_estate.fosnr:
                if not municipality.published:
                    raise NotImplementedError
                extract_raw = self._extract_reader_.read(real_estate, municipality.logo)
                extract = self.plr_tolerance_check(extract_raw)
                return extract.to_extract()
        raise NoResultFound()
