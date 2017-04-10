# -*- coding: utf-8 -*-
import json
import optparse

import pkg_resources
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyramid_oereb.lib.config import parse
from pyramid_oereb.models import Plr119Office, Plr119Geometry, Plr119PublicLawRestriction, \
    Plr119ViewService, Plr119PublicLawRestrictionDocument, Plr119DocumentBase, Plr119LegalProvision


def load():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create all content for the standard database'
    )
    parser.add_option(
        '-c', '--configuration',
        dest='configuration',
        metavar='YAML',
        type='string',
        help='The absolute path to the configuration yaml file (standard is: pyramid_oereb.yml).'
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


def __load__(configuration, section='pyramid_oereb'):
    config = parse(configuration, section)
    engine = create_engine(config.get('db_connection'), echo=True)
    connection = engine.connect()

    # Truncate tables
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
        Session = sessionmaker(bind=engine)
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

    connection.close()
