# -*- coding: utf-8 -*-
import codecs
import re
import json
import optparse
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard.sources.plr import parse_multiple_standard_themes


class SampleData(object):
    """
    Class for sample data handling.
    """

    def __init__(self, configuration, section='pyramid_oereb', c2ctemplate_style=False,
                 directory='sample_data', sql_file=None):
        """

        Args:
            configuration (str): Path to the configuration yaml file.
            section (str): The used section within the yaml file. Default is `pyramid_oereb`.
            c2ctemplate_style (bool): True if the yaml use a c2c template style (vars.[section]).
                Default is False.
            directory (str): Location of the sample data. Default is `sample_data`.
            sql_file (file): The SQL file to be created. Default is None.
        """
        self._configuration = configuration
        self._section = section
        self._directory = directory
        self._sql_file = sql_file

        Config.init(self._configuration, self._section, c2ctemplate_style)
        self._engine = create_engine(Config.get('app_schema').get('db_connection'), echo=True)
        self._connection = None

    @classmethod
    def _format_value(cls, value):
        """
        Format the value in SQL.

        Args:
            value (str): The value
        Returns:
            str: The formatted value
        """
        if isinstance(value, str) or isinstance(value, bytes):
            return u"'{}'".format(value.replace("'", "''"))
        if isinstance(value, int) or isinstance(value, float):
            return str(value)
        if isinstance(value, bool):
            return "'t'" if value else "'f'"
        if isinstance(value, dict):
            return cls._format_value(json.dumps(value, ensure_ascii=False))
        raise "Unsupported type {}".format(type(value))

    def _do_sql_insert(self, sql, items):
        """
        Write the SQL inserts in a file.

        Args:
            sql (str): The based SQL statement
            items (array): The values
        """
        for k, v in items.items():
            sql = re.sub(r":{}\b".format(re.escape(k)), self._format_value(v), sql)

        for column in re.findall(r":[a-z_0-9]+\b", sql):
            sql = re.sub(r", :?{}\b".format(re.escape(column[1:])), '', sql)
            sql = re.sub(r":?{}, ".format(re.escape(column[1:])), '', sql)

        self._sql_file.write(u"{};\n".format(sql))

    def _has_connection(self):
        """
        Returns True if an active connection is available.

        Returns:
             bool: True if an active connection is available.
        """
        return isinstance(self._connection, Connection) and not self._connection.closed

    def _load_sample(self, class_, import_file_name):
        """
        Load the samples in the database ir in an SQL file.

        Args:
            class_ (sqlalchemy.ext.declarative.ConcreteBase): SQLAlchemy class
            import_file_name (str): The resource file name to import
        """
        with codecs.open(os.path.join(self._directory, import_file_name), encoding='utf-8') as f:
            if self._sql_file is None:
                if self._has_connection():
                    self._connection.execute(class_.__table__.insert(), json.loads(f.read()))
            else:
                sql = str(class_.__table__.insert())
                for r in json.loads(f.read()):
                    self._do_sql_insert(sql, r)

    def _truncate_existing(self, schema):
        """
        Truncates existing tables.
        """

        if self._has_connection():

            # Truncate tables
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Theme.__table__.schema,
                table=schema.Theme.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Logo.__table__.schema,
                table=schema.Logo.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.DocumentTypeText.__table__.schema,
                table=schema.DocumentTypeText.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Glossary.__table__.schema,
                table=schema.Glossary.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.ExclusionOfLiability.__table__.schema,
                table=schema.ExclusionOfLiability.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.GeneralInformation.__table__.schema,
                table=schema.GeneralInformation.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Municipality.__table__.schema,
                table=schema.Municipality.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Address.__table__.schema,
                table=schema.Address.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.RealEstate.__table__.schema,
                table=schema.RealEstate.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.RealEstateType.__table__.schema,
                table=schema.RealEstateType.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.PublicLawRestrictionDocument.__table__.schema,
                table=schema.PublicLawRestrictionDocument.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Document.__table__.schema,
                table=schema.Document.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Geometry.__table__.schema,
                table=schema.Geometry.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.PublicLawRestriction.__table__.schema,
                table=schema.PublicLawRestriction.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.ViewService.__table__.schema,
                table=schema.ViewService.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Office.__table__.schema,
                table=schema.Office.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.Availability.__table__.schema,
                table=schema.Availability.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.LegendEntry.__table__.schema,
                table=schema.LegendEntry.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.DataIntegration.__table__.schema,
                table=schema.DataIntegration.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.LawStatus.__table__.schema,
                table=schema.LawStatus.__table__.name
            ))

    def load(self):
        """
        Performs the database operations to load the sample data.
        """
        # Find data model for each PLR from config
        themes = parse_multiple_standard_themes(Config)
        contaminated_public_transport_sites = themes['ContaminatedPublicTransportSites']
        groundwater_protection_zones = themes['GroundwaterProtectionZones']
        motorways_building_lines = themes['MotorwaysBuildingLines']
        contaminated_military_sites = themes['ContaminatedMilitarySites']
        forest_perimeters = themes['ForestPerimeters']

        from pyramid_oereb.standard.models.main import Theme, Logo, DocumentTypeText, RealEstate, Address, \
            Municipality, Glossary, ExclusionOfLiability, GeneralInformation, RealEstateType, LawStatus

        if self._sql_file is None:
            self._connection = self._engine.connect()

        try:

            # Fill tables with sample data
            for class_, file_name in [
                (Theme, 'themes.json'),
                (Logo, 'logo.json'),
                (DocumentTypeText, 'document_types.json'),
                (RealEstate, 'real_estates.json'),
                (Address, 'addresses.json'),
                (Municipality, 'municipalities.json'),
                (Glossary, 'glossary.json'),
                (ExclusionOfLiability, 'exclusion_of_liability.json'),
                (LawStatus, 'law_status.json'),
                (RealEstateType, 'real_estate_type.json'),
                (GeneralInformation, 'general_information.json')
            ]:
                self._load_sample(class_, file_name)

            for schema, folder in [
                (contaminated_public_transport_sites, "contaminated_public_transport_sites"),
                (groundwater_protection_zones, "groundwater_protection_zones"),
                (forest_perimeters, "forest_perimeters"),
                (motorways_building_lines, "motorways_building_lines"),
                (contaminated_military_sites, "contaminated_military_sites"),
            ]:
                print("Import theme {}.".format(folder))
                # Truncate existing tables
                self._truncate_existing(schema)

                for class_, file_name in [
                    (schema.Availability, 'availabilities.json'),
                    (schema.Office, 'office.json'),
                    (schema.DataIntegration, 'data_integration.json'),
                    (schema.ViewService, 'view_service.json'),
                    (schema.LegendEntry, 'legend_entry.json'),
                    (schema.PublicLawRestriction, 'public_law_restriction.json'),
                    (schema.Geometry, 'geometry.json'),
                    (schema.Document, 'document.json')
                ]:
                    self._load_sample(class_, os.path.join(folder, file_name))

                if hasattr(schema, 'PublicLawRestrictionDocument'):
                    for class_, file_name in [
                        (schema.PublicLawRestrictionDocument, 'public_law_restriction_document.json')
                    ]:
                        self._load_sample(class_, os.path.join(folder, file_name))

        finally:
            if self._has_connection():
                self._connection.close()


def _run():
    """
    Loads sample data from the json files with the repository. The method can be called by running
    'load_sample_data' from the virtual environment. Check 'load_sample_data --help' for available options.
    """
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Loads sample data into the configured database.'
    )
    parser.add_option(
        '-c', '--configuration',
        dest='configuration',
        metavar='YAML',
        type='string',
        help='The absolute path to the configuration yaml file.'
    )
    parser.add_option(
        '-s', '--section',
        dest='section',
        metavar='SECTION',
        type='string',
        default='pyramid_oereb',
        help='The section which contains configruation (default is: pyramid_oereb).'
    )
    parser.add_option(
        '-d', '--dir',
        dest='directory',
        metavar='DIRECTORY',
        type='string',
        default='sample_data',
        help='The directory containing the sample data (default is: sample_data).'
    )
    parser.add_option(
        '--sql-file',
        type='string',
        help='Generate an SQL file.'
    )
    parser.add_option(
        '--c2ctemplate-style',
        dest='c2ctemplate_style',
        action='store_true',
        default=False,
        help='Is the yaml file using a c2ctemplate style (starting with vars)'
    )
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    if options.sql_file is None:
        SampleData(
            options.configuration,
            section=options.section,
            c2ctemplate_style=options.c2ctemplate_style,
            directory=options.directory
        ).load()
    else:
        with codecs.open(options.sql_file, mode='w', encoding='utf-8') as sql_file:
            SampleData(
                options.configuration,
                section=options.section,
                c2ctemplate_style=options.c2ctemplate_style,
                directory=options.directory,
                sql_file=sql_file
            ).load()


if __name__ == '__main__':
    _run()
