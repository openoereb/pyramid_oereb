# -*- coding: utf-8 -*-

import re
import json
import optparse

import pkg_resources
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, class_mapper

from pyramid_oereb.lib.config import parse
from pyramid_oereb.standard.models.contaminated_public_transport_sites import Office, Geometry, \
    PublicLawRestriction, ViewService, PublicLawRestrictionDocument, DocumentBase, LegalProvision, \
    Availability, LegendEntry
from pyramid_oereb.standard.models.main import RealEstate, Address, Municipality


def load_standard_sample():
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
        '--sql-file',
        type='string',
        help='Generate an SQL file.'
    )
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    if options.sql_file is None:
        _load_standard_sample(configuration=options.configuration, section=options.section)
    else:
        with open(options.sql_file, 'w') as sql_file:
            _load_standard_sample(
                configuration=options.configuration, section=options.section, sql_file=sql_file)


def _format_value(value):
    """
    Format the value in SQL.

    Args:
        value (str): The value
    Returns:
        str: The formatted value
    """
    if isinstance(value, str) or isinstance(value, unicode):
        return u"'{}'".format(value.replace("'", "''"))
    if isinstance(value, int) or isinstance(value, float):
        return str(value)
    if isinstance(value, bool):
        return "'t'" if value else "'f'"
    if isinstance(value, dict):
        return _format_value(json.dumps(value))
    raise "Unsupported type {}".format(type(value))


def _do_sql_insert(sql, items, sql_file):
    """
    Write the SQL inserts in a file.

    # Create database connection
    config = parse(configuration, section)
    engine = create_engine(config.get('app_schema').get('db_connection'), echo=True)
    connection = engine.connect()

    # Truncate tables
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Municipality.__table__.schema,
        table=Municipality.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Address.__table__.schema,
        table=Address.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=RealEstate.__table__.schema,
        table=RealEstate.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PublicLawRestrictionDocument.__table__.schema,
        table=PublicLawRestrictionDocument.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=DocumentBase.__table__.schema,
        table=DocumentBase.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Geometry.__table__.schema,
        table=Geometry.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PublicLawRestriction.__table__.schema,
        table=PublicLawRestriction.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=ViewService.__table__.schema,
        table=ViewService.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Office.__table__.schema,
        table=Office.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Availability.__table__.schema,
        table=Availability.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LegendEntry.__table__.schema,
        table=LegendEntry.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=DataIntegration.__table__.schema,
        table=DataIntegration.__table__.name
    ))

    Args:
        sql (str): The based SQL statement
        items (array): The values
        sql_file (file): The SQL file
    """
    for k, v in items.items():
        sql = re.sub(r":{}\b".format(re.escape(k)), _format_value(v), sql)

    for column in re.findall(r":[a-z_0-9]+\b", sql):
        sql = re.sub(r", :?{}\b".format(re.escape(column[1:])), '', sql)
        sql = re.sub(r":?{}, ".format(re.escape(column[1:])), '', sql)

    sql_file.write(u"{};\n".format(sql).encode('utf-8'))


def _load_sample(class_, import_file_name, connection, sql_file=None):
    """
    Load the samples in the database ir in an SQL file.

    Args:
        class_ (sqlalchemy.ext.declarative.ConcreteBase): SQLAlchemy class
        import_file_name (str): The resource file name to import
        connection (sqlalchemy.engine.Connection): The connection
        sql_file (file): The SQL file
    """
    with open(pkg_resources.resource_filename('tests', import_file_name)) as f:
        if sql_file is None:
            connection.execute(class_.__table__.insert(), json.loads(f.read()))
        else:
            sql = str(class_.__table__.insert())
            for r in json.loads(f.read()):
                _do_sql_insert(sql, r, sql_file)


def _load_standard_sample(configuration, section='pyramid_oereb', sql_file=None):
    """
    Performs the database operations to load the sample data.

    Args:
        configuration (str): Path to the configuration yaml file.
        section (str): The used section within the yaml file.
    """

    # Create database connection
    if sql_file is None:
        config = parse(configuration, section)
        engine = create_engine(config.get('app_schema').get('db_connection'), echo=True)
        connection = engine.connect()

        # Truncate tables
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=Municipality.__table__.schema,
            table=Municipality.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=Address.__table__.schema,
            table=Address.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=RealEstate.__table__.schema,
            table=RealEstate.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=PublicLawRestrictionDocument.__table__.schema,
            table=PublicLawRestrictionDocument.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=DocumentBase.__table__.schema,
            table=DocumentBase.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=Geometry.__table__.schema,
            table=Geometry.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=PublicLawRestriction.__table__.schema,
            table=PublicLawRestriction.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=ViewService.__table__.schema,
            table=ViewService.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=Office.__table__.schema,
            table=Office.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=Availability.__table__.schema,
            table=Availability.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=LegendEntry.__table__.schema,
            table=LegendEntry.__table__.name
        ))
    else:
        connection = None

    # Fill tables with sample data
    _load_sample(Availability, 'resources/plr119/availabilities.json', connection, sql_file)
    _load_sample(Office, 'resources/plr119/office.json', connection, sql_file)
    _load_sample(ViewService, 'resources/plr119/view_service.json', connection, sql_file)
    _load_sample(LegendEntry, 'resources/plr119/legend_entry.json', connection, sql_file)
    _load_sample(PublicLawRestriction, 'resources/plr119/public_law_restriction.json', connection, sql_file)
    _load_sample(Geometry, 'resources/plr119/geometry.json', connection, sql_file)

    with open(pkg_resources.resource_filename(
            'tests',
            'resources/plr119/legal_provision.json'
    )) as f:
        lps = json.loads(f.read())
        if sql_file is None:
            Session = sessionmaker(bind=engine)  # Use session because of table inheritance
            session = Session()
            for lp in lps:
                session.add(LegalProvision(**lp))
            session.commit()
            session.close()
        else:
            for lp in lps:
                for table_name in ['document_base', 'document', 'legal_provision']:
                    table = [t for t in class_mapper(LegalProvision).tables if t.name == table_name][0]
                    data = {
                        'type': 'legal_provision'
                    }
                    data.update(lp)
                    _do_sql_insert(str(table.insert()), data, sql_file)

    _load_sample(
        PublicLawRestrictionDocument, 'resources/plr119/public_law_restriction_document.json',
        connection, sql_file)
    _load_sample(RealEstate, 'resources/real_estates.json', connection, sql_file)
    _load_sample(Address, 'resources/addresses.json', connection, sql_file)
    _load_sample(
        Municipality, 'resources/municipalities_with_logo.json', connection, sql_file)

    # Close database connection
    if sql_file is None:
        connection.close()
