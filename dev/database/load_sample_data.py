# -*- coding: utf-8 -*-
import codecs
import re
import json
import optparse
import os
import uuid

from pyramid_oereb.core.config import Config
from pyramid_oereb.contrib.data_sources.standard.sources.plr import parse_multiple_standard_themes


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
        if value is None:
            return "NULL"
        raise LookupError("Unsupported type {}".format(type(value)))

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

    def _load_sample(self, class_, import_file_name):
        """
        Load the samples in the database ir in an SQL file.

        Args:
            class_ (sqlalchemy.ext.declarative.ConcreteBase): SQLAlchemy class
            import_file_name (str): The resource file name to import
        """
        with codecs.open(os.path.join(self._directory, import_file_name), encoding='utf-8') as f:
            sql = str(class_.__table__.insert())
            for r in json.load(f):
                if hasattr(class_, 'id'):
                    if r.get('id') is None:
                        r['id'] = str(uuid.uuid4())
                self._do_sql_insert(sql, r)

    def load(self):
        """
        Performs the database operations to load the sample data.
        """
        # Find data model for each PLR from config
        themes = parse_multiple_standard_themes(Config)
        contaminated_public_transport_sites = themes['ch.BelasteteStandorteOeffentlicherVerkehr']
        land_use_plans = themes['ch.Nutzungsplanung']
        groundwater_protection_zones = themes['ch.Grundwasserschutzzonen']
        motorways_building_lines = themes['ch.BaulinienNationalstrassen']
        contaminated_military_sites = themes['ch.BelasteteStandorteMilitaer']
        forest_perimeters = themes['ch.StatischeWaldgrenzen']

        from pyramid_oereb.contrib.data_sources.standard.models.main import Theme, Logo, \
            DocumentTypeText, RealEstate, Address, Municipality, Glossary, Disclaimer, \
            GeneralInformation, RealEstateType, LawStatus, Document, Office, ThemeDocument, Availability, \
            DataIntegration

        # Fill tables with sample data
        for class_, file_name in [
            (Theme, 'ch.themes.json'),
            (Theme, 'dev.themes.json'),
            (Logo, 'ch.logo.json'),
            (Logo, 'dev.logo.json'),
            (DocumentTypeText, 'ch.document_type.json'),
            (RealEstate, 'dev.real_estates.json'),
            (Address, 'dev.addresses.json'),
            (Municipality, 'dev.municipalities.json'),
            (Glossary, 'ch.glossary.json'),
            (Disclaimer, 'ch.disclaimer.json'),
            (LawStatus, 'ch.law_status.json'),
            (RealEstateType, 'ch.real_estate_type.json'),
            (GeneralInformation, 'ch.general_information.json'),
            (Office, 'ch.law_responsible_offices.json'),
            (Office, 'dev.law_responsible_offices.json'),
            (Document, 'ch.laws.json'),
            (Document, 'dev.laws.json'),
            (ThemeDocument, 'ch.themes_docs.json'),
            (ThemeDocument, 'dev.themes_docs.json'),
            (Availability, 'dev.availabilities.json'),
            (Office, 'dev.data_integration_responsible_offices.json'),
            (DataIntegration, 'dev.data_integration.json')
        ]:
            self._load_sample(class_, file_name)

        for schema, folder in [
            (contaminated_public_transport_sites, "contaminated_public_transport_sites"),
            (land_use_plans, "land_use_plans"),
            (groundwater_protection_zones, "groundwater_protection_zones"),
            (forest_perimeters, "forest_perimeters"),
            (motorways_building_lines, "motorways_building_lines"),
            (contaminated_military_sites, "contaminated_military_sites"),
        ]:
            print("Import theme {}.".format(folder))

            for class_, file_name in [
                (schema.Office, 'office.json'),
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
