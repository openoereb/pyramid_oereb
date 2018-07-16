# -*- coding: utf-8 -*-
import codecs
import sys
import re
import json
import optparse
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker, class_mapper

from pyramid_oereb.lib.config import parse
from pyramid_oereb.standard.models import contaminated_public_transport_sites, \
    groundwater_protection_zones, forest_perimeters
from pyramid_oereb.standard.models.main import RealEstate, Address, Municipality, Glossary


class SampleData(object):
    """
    Class for sample data handling.
    """

    def __init__(self, configuration, section='pyramid_oereb', directory='sample_data', sql_file=None):
        """

        Args:
            configuration (str): Path to the configuration yaml file.
            section (str): The used section within the yaml file. Default is `pyramid_oereb`.
            directory (str): Location of the sample data. Default is `sample_data`.
            sql_file (file): The SQL file to be created. Default is None.
        """
        self._configuration = configuration
        self._section = section
        self._directory = directory
        self._sql_file = sql_file

        config = parse(self._configuration, self._section)
        self._engine = create_engine(config.get('app_schema').get('db_connection'), echo=True)
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
        if sys.version_info.major == 2 and (isinstance(value, str) or isinstance(value, unicode)):  # noqa
            return u"'{}'".format(value.replace("'", "''"))
        if sys.version_info.major > 2 and (isinstance(value, str) or isinstance(value, bytes)):
            return u"'{}'".format(value.replace("'", "''"))
        if isinstance(value, int) or isinstance(value, float):
            return str(value)
        if isinstance(value, bool):
            return "'t'" if value else "'f'"
        if isinstance(value, dict):
            return cls._format_value(json.dumps(value))
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
                schema=schema.Glossary.__table__.schema,
                table=schema.Glossary.__table__.name
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
                schema=schema.PublicLawRestrictionDocument.__table__.schema,
                table=schema.PublicLawRestrictionDocument.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.DocumentReference.__table__.schema,
                table=schema.DocumentReference.__table__.name
            ))
            self._connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=schema.DocumentBase.__table__.schema,
                table=schema.DocumentBase.__table__.name
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

    def load(self):
        """
        Performs the database operations to load the sample data.
        """

        if self._sql_file is None:
            self._connection = self._engine.connect()

        try:

            for schema, folder in [
                (contaminated_public_transport_sites, "contaminated_public_transport_sites"),
                (groundwater_protection_zones, "groundwater_protection_zones"),
                (forest_perimeters, "forest_perimeters"),
            ]:
                print("Import theme {}.".format(folder))
                # Truncate exisiting tables
                self._truncate_existing(schema)

                # Fill tables with sample data
                for class_, file_name in [
                    (schema.Availability, 'availabilities.json'),
                    (schema.Office, 'office.json'),
                    (schema.DataIntegration, 'data_integration.json'),
                    (schema.ViewService, 'view_service.json'),
                    (schema.LegendEntry, 'legend_entry.json'),
                    (schema.PublicLawRestriction, 'public_law_restriction.json'),
                    (schema.Geometry, 'geometry.json'),
                ]:
                    self._load_sample(class_, os.path.join('plr119', folder, file_name))

                with open(os.path.join(self._directory, 'plr119', folder, 'document.json')) as f:
                    lps = json.loads(f.read())
                    if self._sql_file is None:
                        Session = sessionmaker(bind=self._engine)  # Use session because of table inheritance
                        session = Session()
                        for lp in lps:
                            session.add(schema.Document(**lp))
                        session.commit()
                        session.close()
                    else:
                        for lp in lps:
                            for table_name in ['document_base', 'document']:
                                table = [
                                    t for t in class_mapper(schema.Document).tables if t.name == table_name
                                ][0]
                                data = {
                                    'type': 'document'
                                }
                                data.update(lp)
                                self._do_sql_insert(str(table.insert()), data)

                for class_, file_name in [
                    (schema.PublicLawRestrictionDocument, 'public_law_restriction_document.json'),
                    (schema.DocumentReference, 'document_reference.json'),
                ]:
                    self._load_sample(class_, os.path.join('plr119', folder, file_name))
            for class_, file_name in [
                (RealEstate, 'real_estates.json'),
                (Address, 'addresses.json'),
                (Municipality, 'municipalities_with_logo.json'),
                (Glossary, 'glossary.json'),
            ]:
                self._load_sample(class_, file_name)

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
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    if options.sql_file is None:
        SampleData(options.configuration, section=options.section, directory=options.directory).load()
    else:
        with codecs.open(options.sql_file, mode='w', encoding='utf-8') as sql_file:
            SampleData(
                options.configuration,
                section=options.section,
                directory=options.directory,
                sql_file=sql_file
            ).load()


if __name__ == '__main__':
    _run()
