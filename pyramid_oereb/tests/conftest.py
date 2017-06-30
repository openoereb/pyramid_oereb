# -*- coding: utf-8 -*-
import base64
from contextlib import contextmanager

from datetime import date, timedelta

from mako.lookup import TemplateLookup
from pyramid.path import DottedNameResolver, AssetResolver
from pyramid.testing import DummyRequest, testConfig
import pytest
from sqlalchemy import create_engine

from pyramid_oereb import ExtractReader, route_prefix
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import ExclusionOfLiabilityReader
from pyramid_oereb import GlossaryReader
from pyramid_oereb import Processor
from pyramid_oereb import RealEstateReader
from pyramid_oereb.standard.models.motorways_building_lines import Geometry as LineGeometry, \
    PublicLawRestriction as LinePublicLawRestriction, Office as LineOffice, ViewService as LineViewService, \
    Document as LineDocument, DocumentBase as LineDocumentBase, \
    PublicLawRestrictionDocument as LinePublicLawRestrictionDocument, \
    DocumentReference as LineDocumentReference
from pyramid_oereb.standard.models import contaminated_sites
from pyramid_oereb.standard.models import land_use_plans
from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard.models.main import Municipality, Glossary, RealEstate
from pyramid_oereb.views import webservice

pyramid_oereb_test_yml = 'pyramid_oereb/standard/pyramid_oereb.yml'

params = [
    {
        'flavour': 'INVALIDFLAVOUR',
        'format': 'xml',
        'param1': 'egrid'
    },
    {
        'flavour': 'reduced',
        'format': 'INVALIDFORMAT',
        'param1': 'egrid'
    },
    {
        'flavour': 'FULL',
        'format': 'XML',
        'param1': 'egrid'
    },
    {
        'flavour': 'SIGNED',
        'format': 'JSON',
        'param1': 'egrid'
    },
    {
        'flavour': 'EMBEDDABLE',
        'format': 'PDF',
        'param1': 'egrid'
    },
    {
        'flavour': 'full',
        'format': 'PDF',
        'param1': 'GEOMETRY',
        'param2': 'egrid'
    }
]


@pytest.fixture
def xml_templates():
    a = AssetResolver('pyramid_oereb')
    resolver = a.resolve('lib/renderer/extract/templates/xml')
    templates = TemplateLookup(
        directories=[resolver.abspath()],
        output_encoding='utf-8',
        input_encoding='utf-8'
    )
    return templates


@pytest.fixture
def xml_schema():
    a = AssetResolver('pyramid_oereb')
    resolver = a.resolve('tests/resources/Extract.xsd')
    return open(resolver.abspath())


@pytest.fixture(scope='module')
def config():
    Config._config = None
    Config.init(pyramid_oereb_test_yml, 'pyramid_oereb')
    return Config


@contextmanager
def pyramid_oereb_test_config():
    with testConfig() as pyramid_config:
        pyramid_config.add_route('{0}/image/logo'.format(route_prefix), '/image/logo/{logo}')
        pyramid_config.add_view(webservice.Logo, attr='get_image',
                                route_name='{0}/image/logo'.format(route_prefix), request_method='GET')

        pyramid_config.add_route('{0}/image/municipality'.format(route_prefix), '/image/municipality/{fosnr}')
        pyramid_config.add_view(webservice.Municipality, attr='get_image',
                                route_name='{0}/image/municipality'.format(route_prefix),
                                request_method='GET')

        pyramid_config.add_route('{0}/image/symbol'.format(route_prefix),
                                 '/image/symbol/{theme_code}/{type_code}')
        pyramid_config.add_view(webservice.Symbol, attr='get_image',
                                route_name='{0}/image/symbol'.format(route_prefix), request_method='GET')

        yield pyramid_config


class MockRequest(DummyRequest):
    def __init__(self):
        super(MockRequest, self).__init__()

        Config._config = None
        Config.init(pyramid_oereb_test_yml, 'pyramid_oereb')

        real_estate_config = Config.get_real_estate_config()
        municipality_config = Config.get_municipality_config()
        exclusion_of_liability_config = Config.get_exclusion_of_liability_config()
        glossary_config = Config.get_glossary_config()
        logos = Config.get_logo_config()
        plr_cadastre_authority = Config.get_plr_cadastre_authority()

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
        for plr in Config.get('plrs'):
            plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
            plr_sources.append(plr_source_class(**plr))

        extract_reader = ExtractReader(
            plr_sources,
            plr_cadastre_authority,
            logos
        )
        self.processor = Processor(
            real_estate_reader=real_estate_reader,
            municipality_reader=municipality_reader,
            exclusion_of_liability_reader=exclusion_of_liability_reader,
            glossary_reader=glossary_reader,
            plr_sources=plr_sources,
            extract_reader=extract_reader,
        )

    @property
    def pyramid_oereb_processor(self):
        return self.processor


@pytest.fixture(scope='module')
def connection(config):
    engine = create_engine(config.get('app_schema').get('db_connection'))
    connection_ = engine.connect()

    # Truncate tables
    connection_.execute('TRUNCATE {schema}.{table};'.format(
        schema=Municipality.__table__.schema,
        table=Municipality.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table};'.format(
        schema=Glossary.__table__.schema,
        table=Glossary.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table};'.format(
        schema=RealEstate.__table__.schema,
        table=RealEstate.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineGeometry.__table__.schema,
        table=LineGeometry.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LinePublicLawRestriction.__table__.schema,
        table=LinePublicLawRestriction.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineOffice.__table__.schema,
        table=LineOffice.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineViewService.__table__.schema,
        table=LineViewService.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineDocument.__table__.schema,
        table=LineDocument.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineDocumentBase.__table__.schema,
        table=LineDocumentBase.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LinePublicLawRestrictionDocument.__table__.schema,
        table=LinePublicLawRestrictionDocument.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=LineDocumentReference.__table__.schema,
        table=LineDocumentReference.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=contaminated_sites.LegendEntry.__table__.schema,
        table=contaminated_sites.LegendEntry.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=contaminated_sites.ViewService.__table__.schema,
        table=contaminated_sites.ViewService.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=contaminated_sites.Office.__table__.schema,
        table=contaminated_sites.Office.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=contaminated_sites.PublicLawRestriction.__table__.schema,
        table=contaminated_sites.PublicLawRestriction.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=contaminated_sites.Geometry.__table__.schema,
        table=contaminated_sites.Geometry.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=land_use_plans.ViewService.__table__.schema,
        table=land_use_plans.ViewService.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=land_use_plans.Office.__table__.schema,
        table=land_use_plans.Office.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=land_use_plans.PublicLawRestriction.__table__.schema,
        table=land_use_plans.PublicLawRestriction.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=land_use_plans.Geometry.__table__.schema,
        table=land_use_plans.Geometry.__table__.name
    ))

    # Add dummy municipality
    connection_.execute(Municipality.__table__.insert(), {
        'fosnr': 1234,
        'name': 'Test',
        'published': True,
        'logo': base64.b64encode('abcdefg'),
        'geom': 'SRID=2056;MULTIPOLYGON(((0 0, 0 10, 10 10, 10 0, 0 0)))'
    })

    # Add dummy glossary
    connection_.execute(Glossary.__table__.insert(), {
        'id': 1,
        'title': {'fr': u'SGRF', 'de': u'AGI'},
        'content': {'fr': u'Service de la géomatique et du registre foncier', 'de': u'Amt für Geoinformation'}
    })

    # Add dummy real estate
    connection_.execute(RealEstate.__table__.insert(), {
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
    connection_.execute(RealEstate.__table__.insert(), {
        'id': 2,
        'egrid': u'TEST2',
        'number': u'9999',
        'identdn': u'BLTEST',
        'type': u'RealEstate',
        'canton': u'BL',
        'municipality': u'Liestal',
        'fosnr': 1234,
        'land_registry_area': 9,
        'limit': 'SRID=2056;MULTIPOLYGON(((2 0, 2 3, 5 3, 5 0, 2 0)))'
    })

    # Add dummy PLR data for line geometry
    connection_.execute(LineViewService.__table__.insert(), {
        'id': 1,
        'link_wms': u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&'
                    u'SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png&'
                    u'LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'.format(Config.get('srid'))
    })
    connection_.execute(LineOffice.__table__.insert(), {
        'id': 1,
        'name': {'de': u'Test Office'}
    })
    connection_.execute(LinePublicLawRestriction.__table__.insert(), {
        'id': 1,
        'content': {'de': u'Long line PLR'},
        'topic': u'MotorwaysBuildingLines',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(LinePublicLawRestriction.__table__.insert(), {
        'id': 2,
        'content': {'de': u'Short line PLR'},
        'topic': u'MotorwaysBuildingLines',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(LinePublicLawRestriction.__table__.insert(), {
        'id': 3,
        'content': {'de': u'Double intersection line PLR'},
        'topic': u'MotorwaysBuildingLines',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(LinePublicLawRestriction.__table__.insert(), {
        'id': 4,
        'content': {'de': u'Future geometry'},
        'topic': u'MotorwaysBuildingLines',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(LineGeometry.__table__.insert(), {
        'id': 1,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;LINESTRING (0 0, 2 2)'
    })
    connection_.execute(LineGeometry.__table__.insert(), {
        'id': 2,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 2,
        'office_id': 1,
        'geom': u'SRID=2056;LINESTRING (1.5 1.5, 1.5 2.5)'
    })
    connection_.execute(LineGeometry.__table__.insert(), {
        'id': 3,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 3,
        'office_id': 1,
        'geom': u'SRID=2056;LINESTRING (3 1, 3 4, 6 4, 6 1, 4.5 1)'
    })
    connection_.execute(LineGeometry.__table__.insert(), {
        'id': 4,
        'legal_state': u'inForce',
        'published_from': unicode((date.today() + timedelta(days=7)).isoformat()),
        'public_law_restriction_id': 4,
        'office_id': 1,
        'geom': u'SRID=2056;LINESTRING (0 0, 4 4)'
    })
    connection_.execute(LineDocumentBase.__table__.insert(), {
        'id': 1,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'type': u'document'
    })
    connection_.execute(LineDocument.__table__.insert(), {
        'id': 1,
        'title': {'de': u'First level document'},
        'office_id': 1
    })
    connection_.execute(LineDocumentBase.__table__.insert(), {
        'id': 2,
        'legal_state': u'inForce',
        'published_from': unicode((date.today() + timedelta(days=7)).isoformat()),
        'type': u'document'
    })
    connection_.execute(LineDocument.__table__.insert(), {
        'id': 2,
        'title': {'de': u'First level future document'},
        'office_id': 1
    })
    connection_.execute(LineDocumentBase.__table__.insert(), {
        'id': 3,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'type': u'document'
    })
    connection_.execute(LineDocument.__table__.insert(), {
        'id': 3,
        'title': {'de': u'Second level document'},
        'office_id': 1
    })
    connection_.execute(LineDocumentBase.__table__.insert(), {
        'id': 4,
        'legal_state': u'inForce',
        'published_from': unicode((date.today() + timedelta(days=7)).isoformat()),
        'type': u'document'
    })
    connection_.execute(LineDocument.__table__.insert(), {
        'id': 4,
        'title': {'de': u'Second level future document'},
        'office_id': 1
    })
    connection_.execute(LinePublicLawRestrictionDocument.__table__.insert(), {
        'id': 1,
        'public_law_restriction_id': 1,
        'document_id': 1
    })
    connection_.execute(LinePublicLawRestrictionDocument.__table__.insert(), {
        'id': 2,
        'public_law_restriction_id': 1,
        'document_id': 2
    })
    connection_.execute(LineDocumentReference.__table__.insert(), {
        'id': 1,
        'document_id': 1,
        'reference_document_id': 3
    })
    connection_.execute(LineDocumentReference.__table__.insert(), {
        'id': 2,
        'document_id': 1,
        'reference_document_id': 4
    })

    # Add dummy PLR data for polygon geometry
    connection_.execute(contaminated_sites.ViewService.__table__.insert(), {
        'id': 1,
        'link_wms': u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&'
                    u'SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png&'
                    u'LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'.format(Config.get('srid'))
    })

    connection_.execute(contaminated_sites.LegendEntry.__table__.insert(), {
        'id': 1,
        'symbol': base64.b64encode(bin(1)),
        'legend_text': {
            'de': u'Test'
        },
        'type_code': u'test',
        'type_code_list': u'type_code_list',
        'topic': u'ContaminatedSites',
        'view_service_id': 1
    })

    connection_.execute(contaminated_sites.Office.__table__.insert(), {
        'id': 1,
        'name': {'de': u'Test Office'}
    })

    connection_.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
        'id': 1,
        'content': {'de': u'Large polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
        'id': 2,
        'content': {'de': u'Small polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
        'id': 3,
        'content': {'de': u'Double intersection polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
        'id': 4,
        'content': {'de': u'Future PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode((date.today() + timedelta(days=7)).isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })

    connection_.execute(contaminated_sites.Geometry.__table__.insert(), {
        'id': 1,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))'
    })
    connection_.execute(contaminated_sites.Geometry.__table__.insert(), {
        'id': 2,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 2,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))'
    })
    connection_.execute(contaminated_sites.Geometry.__table__.insert(), {
        'id': 3,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 3,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION('
                u'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
    })
    connection_.execute(contaminated_sites.Geometry.__table__.insert(), {
        'id': 4,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 4,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 2, 2 2, 2 0, 0 0)))'
    })

    # Add dummy PLR data for collection geometry test
    connection_.execute(land_use_plans.ViewService.__table__.insert(), {
        'id': 1,
        'link_wms': u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&'
                    u'SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png&'
                    u'LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'.format(Config.get('srid'))
    })

    connection_.execute(land_use_plans.Office.__table__.insert(), {
        'id': 1,
        'name': {'de': u'Test Office'}
    })

    connection_.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
        'id': 1,
        'content': {'de': u'Large polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
        'id': 2,
        'content': {'de': u'Small polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
        'id': 3,
        'content': {'de': u'Double intersection polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
        'id': 4,
        'content': {'de': u'Future PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode((date.today() + timedelta(days=7)).isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })

    connection_.execute(land_use_plans.Geometry.__table__.insert(), {
        'id': 1,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION('
                u'POLYGON((1 -1, 9 -1, 9 7, 1 7, 1 8, 10 8, 10 -2, 1 -2, 1 -1)))'
    })
    connection_.execute(land_use_plans.Geometry.__table__.insert(), {
        'id': 2,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))'
    })
    connection_.execute(land_use_plans.Geometry.__table__.insert(), {
        'id': 3,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION('
                u'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
    })
    connection_.execute(land_use_plans.Geometry.__table__.insert(), {
        'id': 4,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))'
    })
    connection_.execute(land_use_plans.Geometry.__table__.insert(), {
        'id': 5,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;GEOMETRYCOLLECTION(POINT(1 2))'
    })

    connection_.close()
    yield connection_
