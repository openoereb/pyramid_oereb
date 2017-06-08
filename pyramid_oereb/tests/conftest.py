# -*- coding: utf-8 -*-
import base64

from datetime import date, timedelta
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
    PublicLawRestriction as LinePublicLawRestriction, Office as LineOffice, ViewService as LineViewService, \
    Document as LineDocument, DocumentBase as LineDocumentBase, \
    PublicLawRestrictionDocument as LinePublicLawRestrictionDocument, \
    DocumentReference as LineDocumentReference
from pyramid_oereb.standard.models.contaminated_sites import Geometry as PolyGeometry, \
    PublicLawRestriction as PolyPublicLawRestriction, Office as PolyOffice, ViewService as PolyViewService
from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard.models.main import Municipality, Glossary, RealEstate


pyramid_oereb_test_yml = 'pyramid_oereb/standard/pyramid_oereb.yml'


@pytest.fixture(scope='module')
def config():
    Config._config = None
    Config.init(pyramid_oereb_test_yml, 'pyramid_oereb')
    return Config


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
        schema=PolyGeometry.__table__.schema,
        table=PolyGeometry.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PolyPublicLawRestriction.__table__.schema,
        table=PolyPublicLawRestriction.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PolyOffice.__table__.schema,
        table=PolyOffice.__table__.name
    ))
    connection_.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
        schema=PolyViewService.__table__.schema,
        table=PolyViewService.__table__.name
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
                    u'SRS=EPSG:21781&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png&'
                    u'LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
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
    connection_.execute(PolyViewService.__table__.insert(), {
        'id': 1,
        'link_wms': u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&'
                    u'SRS=EPSG:21781&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png&'
                    u'LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
    })
    connection_.execute(PolyOffice.__table__.insert(), {
        'id': 1,
        'name': {'de': u'Test Office'}
    })
    connection_.execute(PolyPublicLawRestriction.__table__.insert(), {
        'id': 1,
        'content': {'de': u'Large polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(PolyPublicLawRestriction.__table__.insert(), {
        'id': 2,
        'content': {'de': u'Small polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(PolyPublicLawRestriction.__table__.insert(), {
        'id': 3,
        'content': {'de': u'Double intersection polygon PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(PolyPublicLawRestriction.__table__.insert(), {
        'id': 4,
        'content': {'de': u'Future PLR'},
        'topic': u'ContaminatedSites',
        'legal_state': u'inForce',
        'published_from': unicode((date.today() + timedelta(days=7)).isoformat()),
        'view_service_id': 1,
        'office_id': 1
    })
    connection_.execute(PolyGeometry.__table__.insert(), {
        'id': 1,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 1,
        'office_id': 1,
        'geom': u'SRID=2056;POLYGON ((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0))'
    })
    connection_.execute(PolyGeometry.__table__.insert(), {
        'id': 2,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 2,
        'office_id': 1,
        'geom': u'SRID=2056;POLYGON ((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5))'
    })
    connection_.execute(PolyGeometry.__table__.insert(), {
        'id': 3,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 3,
        'office_id': 1,
        'geom': u'SRID=2056;POLYGON ((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5))'
    })
    connection_.execute(PolyGeometry.__table__.insert(), {
        'id': 4,
        'legal_state': u'inForce',
        'published_from': unicode(date.today().isoformat()),
        'public_law_restriction_id': 4,
        'office_id': 1,
        'geom': u'SRID=2056;POLYGON ((0 0, 0 2, 2 2, 2 0, 0 0))'
    })

    connection_.close()
    yield connection_
