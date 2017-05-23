# -*- coding: utf-8 -*-
import base64

import datetime
from pyramid.path import DottedNameResolver
from pyramid.testing import DummyRequest
import pytest
from sqlalchemy import create_engine

from pyramid_oereb import ExtractReader
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import ExclusionOfLiabilityReader
from pyramid_oereb import GlossaryReader
from pyramid_oereb import Processor
from pyramid_oereb import RealEstateReader
from pyramid_oereb.standard.models.motorways_building_lines import Geometry as LineGeometry, \
    PublicLawRestriction as LinePublicLawRestriction, Office as LineOffice, ViewService as LineViewService
from pyramid_oereb.standard.models.contaminated_sites import Geometry as PolyGeometry, \
    PublicLawRestriction as PolyPublicLawRestriction, Office as PolyOffice, ViewService as PolyViewService
from pyramid_oereb.lib.config import ConfigReader
from pyramid_oereb.standard.models.main import Municipality, Glossary, RealEstate


pyramid_oereb_test_yml = 'pyramid_oereb/tests/resources/pyramid_oereb_test.yml'


@pytest.fixture()
def config_reader():
    return ConfigReader(pyramid_oereb_test_yml, 'pyramid_oereb')


class MockRequest(DummyRequest):
    def __init__(self):
        super(MockRequest, self).__init__()

        self.config_reader = ConfigReader(pyramid_oereb_test_yml, 'pyramid_oereb')

        real_estate_config = self.config_reader.get_real_estate_config()
        municipality_config = self.config_reader.get_municipality_config()
        exclusion_of_liability_config = self.config_reader.get_exclusion_of_liability_config()
        glossary_config = self.config_reader.get_glossary_config()
        logos = self.config_reader.get_logo_config()
        plr_cadastre_authority = self.config_reader.get_plr_cadastre_authority()
        point_types = self.config_reader.get('plr_limits').get('point_types')
        line_types = self.config_reader.get('plr_limits').get('line_types')
        polygon_types = self.config_reader.get('plr_limits').get('polygon_types')
        min_length = self.config_reader.get('plr_limits').get('min_length')
        min_area = self.config_reader.get('plr_limits').get('min_area')

        real_estate_reader = RealEstateReader(
            real_estate_config.get('source').get('class'),
            **real_estate_config.get('source').get('params')
        )

        municipality_reader = MunicipalityReader(
            municipality_config.get('source').get('class'),
            **municipality_config.get('source').get('params')
        )

        exclusion_of_liability_reader = ExclusionOfLiabilityReader(
            exclusion_of_liability_config.get('source').get('class'),
            **exclusion_of_liability_config.get('source').get('params')
        )

        glossary_reader = GlossaryReader(
            glossary_config.get('source').get('class'),
            **glossary_config.get('source').get('params')
        )

        plr_sources = []
        for plr in config_reader.get('plrs'):
            plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
            plr_sources.append(plr_source_class(**plr))

        extract_reader = ExtractReader(
            plr_sources,
            plr_cadastre_authority,
            logos,
            # TODO: Read this from config. Will be solved by: https://jira.camptocamp.com/browse/GSOREB-195
            [{'de': 'Daten der Swisstopo'}, {'de': 'Amtliche Vermessung'}]
        )
        self.processor = Processor(
            real_estate_reader=real_estate_reader,
            municipality_reader=municipality_reader,
            exclusion_of_liability_reader=exclusion_of_liability_reader,
            glossary_reader=glossary_reader,
            plr_sources=plr_sources,
            extract_reader=extract_reader,
            point_types=point_types,
            line_types=line_types,
            polygon_types=polygon_types,
            min_length=min_length,
            min_area=min_area
        )

    @property
    def pyramid_oereb_processor(self):
        return self.processor

    @property
    def pyramid_oereb_config_reader(self):
        return self.config_reader


@pytest.fixture()
def connection(config_reader):
    engine = create_engine(config_reader.get('app_schema').get('db_connection'))
    connection = engine.connect()

    # Add dummy municipality
    connection.execute('TRUNCATE {schema}.{table};'.format(
        schema=Municipality.__table__.schema,
        table=Municipality.__table__.name
    ))
    connection.execute(Municipality.__table__.insert(), {
        'fosnr': 1234,
        'name': 'Test',
        'published': True,
        'logo': base64.b64encode('abcdefg'),
        'geom': 'SRID=2056;MULTIPOLYGON(((0 0, 0 10, 10 10, 10 0, 0 0)))'
    })

    # Add dummy glossary
    connection.execute('TRUNCATE {schema}.{table};'.format(
        schema=Glossary.__table__.schema,
        table=Glossary.__table__.name
    ))
    connection.execute(Glossary.__table__.insert(), {
        'id': 1,
        'title': u'SGRF',
        'content': u'Service de la géomatique et du registre foncier'
    })

    # Add dummy real estate
    connection.execute('TRUNCATE {schema}.{table};'.format(
        schema=RealEstate.__table__.schema,
        table=RealEstate.__table__.name
    ))
    connection.execute(RealEstate.__table__.insert(), {
        'id': 1,
        'egrid': u'TEST',
        'number': u'1000',
        'identdn': u'BLTEST',
        'type': u'RealEstate',
        'canton': u'BL',
        'municipality': u'Liestal',
        'fosnr': 1234,
        'land_registry_area': 4,
        'limit': 'SRID=2056;MULTIPOLYGON(((0 0, 0 2, 2 2, 2 0, 0 0)))'
    })

    # Add dummy PLR data for line geometry
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineGeometry.__table__.schema,
        table=LineGeometry.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LinePublicLawRestriction.__table__.schema,
        table=LinePublicLawRestriction.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineOffice.__table__.schema,
        table=LineOffice.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineViewService.__table__.schema,
        table=LineViewService.__table__.name
    ))
    connection.execute(LineViewService.__table__.insert(), {
        'id': 1,
        'link_wms': u'http://my.wms.com'
    })
    connection.execute(LineOffice.__table__.insert(), {
        'id': 1,
        'name': u'{"de": "Test Office"}'
    })
    connection.execute(LinePublicLawRestriction.__table__.insert(), {
        'id': 1,
        'content': u'{"de": "Long line PLR"}',
        'topic': u'MotorwaysBuildingLines',
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection.execute(LinePublicLawRestriction.__table__.insert(), {
        'id': 2,
        'content': u'{"de": "Short line PLR"}',
        'topic': u'MotorwaysBuildingLines',
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection.execute(LineGeometry.__table__.insert(), {
        'id': 1,
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;LINESTRING (0 0, 2 2)'
    })
    connection.execute(LineGeometry.__table__.insert(), {
        'id': 2,
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'public_law_restriction_id': 2,
        'office_id': 1,
        'geom': u'SRID=2056;LINESTRING (1.5 1.5, 1.5 2.5)'
    })

    # Add dummy PLR data for polygon geometry
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PolyGeometry.__table__.schema,
        table=PolyGeometry.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PolyPublicLawRestriction.__table__.schema,
        table=PolyPublicLawRestriction.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PolyOffice.__table__.schema,
        table=PolyOffice.__table__.name
    ))
    connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PolyViewService.__table__.schema,
        table=PolyViewService.__table__.name
    ))
    connection.execute(PolyViewService.__table__.insert(), {
        'id': 1,
        'link_wms': u'http://my.wms.com'
    })
    connection.execute(PolyOffice.__table__.insert(), {
        'id': 1,
        'name': u'{"de": "Test Office"}'
    })
    connection.execute(PolyPublicLawRestriction.__table__.insert(), {
        'id': 1,
        'content': u'{"de": "Large polygon PLR"}',
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection.execute(PolyPublicLawRestriction.__table__.insert(), {
        'id': 2,
        'content': u'{"de": "Small polygon PLR"}',
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection.execute(PolyGeometry.__table__.insert(), {
        'id': 1,
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;POLYGON ((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0))'
    })
    connection.execute(PolyGeometry.__table__.insert(), {
        'id': 2,
        'legal_state': u'inForce',
        'published_from': unicode(datetime.date.today().isoformat()),
        'public_law_restriction_id': 2,
        'office_id': 1,
        'geom': u'SRID=2056;POLYGON ((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5))'
    })

    connection.close()
    return connection
