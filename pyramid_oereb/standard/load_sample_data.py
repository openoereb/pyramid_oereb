# -*- coding: utf-8 -*-
import json
import optparse

import pkg_resources
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyramid_oereb.lib.config import parse
from pyramid_oereb.models import Plr119Office, Plr119Geometry, Plr119PublicLawRestriction, \
    Plr119ViewService, Plr119PublicLawRestrictionDocument, Plr119DocumentBase, Plr119LegalProvision, \
    Plr119Availability, PyramidOerebMainRealEstate, PyramidOerebMainAddress, PyramidOerebMainMunicipality
from pyramid_oereb.standard.models.contaminated_public_transport_sites import Office, Geometry, \
    PublicLawRestriction, ViewService, PublicLawRestrictionDocument, DocumentBase, LegalProvision, \
    Availability
from pyramid_oereb.standard.models.main import RealEstate, Address, Municipality


def load():
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
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    __load__(configuration=options.configuration, section=options.section)


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
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    _load_standard_sample_(configuration=options.configuration, section=options.section)


def _load_standard_sample_(configuration, section='pyramid_oereb'):
    """
    Performs the database operations to load the sample data.
    :param configuration: Path to the configuration yaml file.
    :type configuration: str
    :param section: The used section within the yaml file.
    :type section: str
    """

    # Create database connection
    config = parse(configuration, section)
    engine = create_engine(config.get('db_connection'), echo=True)
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

    # Fill tables with sample data
    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/availabilities.json'
    )) as f:
        connection.execute(Availability.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/office.json'
    )) as f:
        connection.execute(Office.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/view_service.json'
    )) as f:
        connection.execute(ViewService.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/public_law_restriction.json'
    )) as f:
        connection.execute(PublicLawRestriction.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/geometry.json'
    )) as f:
        connection.execute(Geometry.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/legal_provision.json'
    )) as f:
        lps = json.loads(f.read())
        Session = sessionmaker(bind=engine)  # Use session because of table inheritance
        session = Session()
        for lp in lps:
            session.add(LegalProvision(**lp))
        session.commit()
        session.close()

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/public_law_restriction_document.json'
    )) as f:
        connection.execute(PublicLawRestrictionDocument.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/real_estates.json'
    )) as f:
        connection.execute(RealEstate.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/addresses.json'
    )) as f:
        connection.execute(Address.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/municipalities_with_logo.json'
    )) as f:
        connection.execute(Municipality.__table__.insert(), json.loads(f.read()))

    # Close database connection
    connection.close()


def __load__(configuration, section='pyramid_oereb'):
    """
    Performs the database operations to load the sample data.
    :param configuration: Path to the configuration yaml file.
    :type configuration: str
    :param section: The used section within the yaml file.
    :type section: str
    """

    # Create database connection
    config = parse(configuration, section)
    engine = create_engine(config.get('db_connection'), echo=True)
    connection = engine.connect()

    # Truncate tables
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PyramidOerebMainMunicipality.__table__.schema,
        table=PyramidOerebMainMunicipality.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PyramidOerebMainAddress.__table__.schema,
        table=PyramidOerebMainAddress.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PyramidOerebMainRealEstate.__table__.schema,
        table=PyramidOerebMainRealEstate.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Plr119PublicLawRestrictionDocument.__table__.schema,
        table=Plr119PublicLawRestrictionDocument.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Plr119DocumentBase.__table__.schema,
        table=Plr119DocumentBase.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Plr119Geometry.__table__.schema,
        table=Plr119Geometry.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Plr119PublicLawRestriction.__table__.schema,
        table=Plr119PublicLawRestriction.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Plr119ViewService.__table__.schema,
        table=Plr119ViewService.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Plr119Office.__table__.schema,
        table=Plr119Office.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=Plr119Availability.__table__.schema,
        table=Plr119Availability.__table__.name
    ))

    # Fill tables with sample data
    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/availabilities.json'
    )) as f:
        connection.execute(Plr119Availability.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/office.json'
    )) as f:
        connection.execute(Plr119Office.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/view_service.json'
    )) as f:
        connection.execute(Plr119ViewService.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/public_law_restriction.json'
    )) as f:
        connection.execute(Plr119PublicLawRestriction.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/geometry.json'
    )) as f:
        connection.execute(Plr119Geometry.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/legal_provision.json'
    )) as f:
        lps = json.loads(f.read())
        Session = sessionmaker(bind=engine)  # Use session because of table inheritance
        session = Session()
        for lp in lps:
            session.add(Plr119LegalProvision(**lp))
        session.commit()
        session.close()

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/plr119/public_law_restriction_document.json'
    )) as f:
        connection.execute(Plr119PublicLawRestrictionDocument.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/real_estates.json'
    )) as f:
        connection.execute(PyramidOerebMainRealEstate.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/addresses.json'
    )) as f:
        connection.execute(PyramidOerebMainAddress.__table__.insert(), json.loads(f.read()))

    with open(pkg_resources.resource_filename(
            'pyramid_oereb.tests',
            'resources/municipalities_with_logo.json'
    )) as f:
        connection.execute(PyramidOerebMainMunicipality.__table__.insert(), json.loads(f.read()))

    # Close database connection
    connection.close()
