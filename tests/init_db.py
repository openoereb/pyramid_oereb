# -*- coding: utf-8 -*-
import base64
from datetime import date, timedelta

from sqlalchemy import create_engine

from pyramid_oereb.standard.models import main, contaminated_sites, land_use_plans, motorways_building_lines


class DummyData(object):
    def __init__(self, config):
        assert isinstance(config._config, dict)
        self._config = config
        self._engine = create_engine(self._config.get('app_schema').get('db_connection'))

    def init(self):
        self._truncate()
        self._import_main()
        self._import_motorways_building_lines()
        self._import_contaminated_sites()
        self._import_land_use_plans()

    def _truncate(self):
        connection = self._engine.connect()
        trans = connection.begin()

        # Truncate tables
        connection.execute('TRUNCATE {schema}.{table};'.format(
            schema=main.Address.__table__.schema,
            table=main.Address.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table};'.format(
            schema=main.Municipality.__table__.schema,
            table=main.Municipality.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table};'.format(
            schema=main.Glossary.__table__.schema,
            table=main.Glossary.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table};'.format(
            schema=main.RealEstate.__table__.schema,
            table=main.RealEstate.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.Geometry.__table__.schema,
            table=motorways_building_lines.Geometry.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.PublicLawRestriction.__table__.schema,
            table=motorways_building_lines.PublicLawRestriction.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.Office.__table__.schema,
            table=motorways_building_lines.Office.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.ViewService.__table__.schema,
            table=motorways_building_lines.ViewService.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.Document.__table__.schema,
            table=motorways_building_lines.Document.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.DocumentBase.__table__.schema,
            table=motorways_building_lines.DocumentBase.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.PublicLawRestrictionDocument.__table__.schema,
            table=motorways_building_lines.PublicLawRestrictionDocument.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.DocumentReference.__table__.schema,
            table=motorways_building_lines.DocumentReference.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=motorways_building_lines.DataIntegration.__table__.schema,
            table=motorways_building_lines.DataIntegration.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=contaminated_sites.LegendEntry.__table__.schema,
            table=contaminated_sites.LegendEntry.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=contaminated_sites.ViewService.__table__.schema,
            table=contaminated_sites.ViewService.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=contaminated_sites.Office.__table__.schema,
            table=contaminated_sites.Office.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=contaminated_sites.PublicLawRestriction.__table__.schema,
            table=contaminated_sites.PublicLawRestriction.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=contaminated_sites.Geometry.__table__.schema,
            table=contaminated_sites.Geometry.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=contaminated_sites.DataIntegration.__table__.schema,
            table=contaminated_sites.DataIntegration.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=land_use_plans.ViewService.__table__.schema,
            table=land_use_plans.ViewService.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=land_use_plans.Office.__table__.schema,
            table=land_use_plans.Office.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=land_use_plans.PublicLawRestriction.__table__.schema,
            table=land_use_plans.PublicLawRestriction.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=land_use_plans.Geometry.__table__.schema,
            table=land_use_plans.Geometry.__table__.name
        ))
        connection.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
            schema=land_use_plans.DataIntegration.__table__.schema,
            table=land_use_plans.DataIntegration.__table__.name
        ))

        trans.commit()
        connection.close()

    def _import_main(self):
        connection = self._engine.connect()

        # Add dummy address
        connection.execute(main.Address.__table__.insert(), {
            'street_name': 'test',
            'street_number': '10',
            'zip_code': 4410,
            'geom': 'SRID=2056;POINT(1 1)'
        })

        # Add dummy municipality
        connection.execute(main.Municipality.__table__.insert(), {
            'fosnr': 1234,
            'name': 'Test',
            'published': True,
            'logo': base64.b64encode('abcdefg'.encode('utf-8')).decode('ascii'),
            'geom': 'SRID=2056;MULTIPOLYGON(((0 0, 0 10, 10 10, 10 0, 0 0)))'
        })

        # Add dummy glossary
        connection.execute(main.Glossary.__table__.insert(), {
            'id': '1',
            'title': {u'fr': u'SGRF', u'de': u'AGI'},
            'content': {'fr': u'Service de la géomatique et du registre foncier',
                        'de': u'Amt für Geoinformation'}
        })

        # Add dummy real estate
        connection.execute(main.RealEstate.__table__.insert(), {
            'id': '1',
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
        connection.execute(main.RealEstate.__table__.insert(), {
            'id': '2',
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

        connection.close()

    def _import_motorways_building_lines(self):
        connection = self._engine.connect()

        # Add dummy PLR data for line geometry
        wms_url = u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default' \
                  u'&SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png' \
                  u'&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
        connection.execute(motorways_building_lines.ViewService.__table__.insert(), {
            'id': '1',
            'reference_wms': wms_url.format(self._config.get('srid')),
            'layer_index': 1,
            'layer_opacity': 1.0
        })
        connection.execute(motorways_building_lines.Office.__table__.insert(), {
            'id': '1',
            'name': {'de': u'Test Office'}
        })
        connection.execute(motorways_building_lines.DataIntegration.__table__.insert(), {
            'id': '1',
            'date': u'2017-07-01T00:00:00',
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
            'id': '1',
            'information': {'de': u'Long line PLR'},
            'topic': u'MotorwaysBuildingLines',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
            'id': '2',
            'information': {'de': u'Short line PLR'},
            'topic': u'MotorwaysBuildingLines',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
            'id': '3',
            'information': {'de': u'Double intersection line PLR'},
            'topic': u'MotorwaysBuildingLines',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
            'id': '4',
            'information': {'de': u'Future geometry'},
            'topic': u'MotorwaysBuildingLines',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.Geometry.__table__.insert(), {
            'id': '1',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '1',
            'office_id': '1',
            'geom': u'SRID=2056;LINESTRING (0 0, 2 2)'
        })
        connection.execute(motorways_building_lines.Geometry.__table__.insert(), {
            'id': '2',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '2',
            'office_id': '1',
            'geom': u'SRID=2056;LINESTRING (1.5 1.5, 1.5 2.5)'
        })
        connection.execute(motorways_building_lines.Geometry.__table__.insert(), {
            'id': '3',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '3',
            'office_id': '1',
            'geom': u'SRID=2056;LINESTRING (3 1, 3 4, 6 4, 6 1, 4.5 1)'
        })
        connection.execute(motorways_building_lines.Geometry.__table__.insert(), {
            'id': '4',
            'law_status': u'inForce',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'public_law_restriction_id': '4',
            'office_id': '1',
            'geom': u'SRID=2056;LINESTRING (0 0, 4 4)'
        })
        connection.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
            'id': '1',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'type': u'document'
        })
        connection.execute(motorways_building_lines.Document.__table__.insert(), {
            'id': '1',
            'document_type': u'Law',
            'title': {'de': u'First level document'},
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
            'id': '2',
            'law_status': u'inForce',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'type': u'document'
        })
        connection.execute(motorways_building_lines.Document.__table__.insert(), {
            'id': '2',
            'document_type': u'Law',
            'title': {'de': u'First level future document'},
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
            'id': '3',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'type': u'document'
        })
        connection.execute(motorways_building_lines.Document.__table__.insert(), {
            'id': '3',
            'document_type': u'Law',
            'title': {'de': u'Second level document'},
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
            'id': '4',
            'law_status': u'inForce',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'type': u'document'
        })
        connection.execute(motorways_building_lines.Document.__table__.insert(), {
            'id': '4',
            'document_type': u'Law',
            'title': {'de': u'Second level future document'},
            'office_id': '1'
        })
        connection.execute(motorways_building_lines.PublicLawRestrictionDocument.__table__.insert(), {
            'id': '1',
            'public_law_restriction_id': '1',
            'document_id': '1'
        })
        connection.execute(motorways_building_lines.PublicLawRestrictionDocument.__table__.insert(), {
            'id': '2',
            'public_law_restriction_id': '1',
            'document_id': '2'
        })
        connection.execute(motorways_building_lines.DocumentReference.__table__.insert(), {
            'id': '1',
            'document_id': '1',
            'reference_document_id': '3'
        })
        connection.execute(motorways_building_lines.DocumentReference.__table__.insert(), {
            'id': '2',
            'document_id': '1',
            'reference_document_id': '4'
        })

        connection.close()

    def _import_contaminated_sites(self):
        connection = self._engine.connect()

        # Add dummy PLR data for polygon geometry
        wms_url = u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default' \
                  u'&SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png' \
                  u'&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
        connection.execute(contaminated_sites.ViewService.__table__.insert(), {
            'id': '1',
            'reference_wms': wms_url.format(self._config.get('srid')),
            'layer_index': 1,
            'layer_opacity': 1.0
        })

        connection.execute(contaminated_sites.LegendEntry.__table__.insert(), {
            'id': '1',
            'symbol': base64.b64encode('1'.encode('utf-8')).decode('ascii'),
            'legend_text': {
                'de': u'Test'
            },
            'type_code': u'test',
            'type_code_list': u'type_code_list',
            'topic': u'ContaminatedSites',
            'view_service_id': '1'
        })

        connection.execute(contaminated_sites.Office.__table__.insert(), {
            'id': '1',
            'name': {'de': u'Test Office'}
        })

        connection.execute(contaminated_sites.DataIntegration.__table__.insert(), {
            'id': '1',
            'date': u'2017-07-01T00:00:00',
            'office_id': '1'
        })

        connection.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
            'id': '1',
            'information': {'de': u'Large polygon PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
            'id': '2',
            'information': {'de': u'Small polygon PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
            'id': '3',
            'information': {'de': u'Double intersection polygon PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(contaminated_sites.PublicLawRestriction.__table__.insert(), {
            'id': '4',
            'information': {'de': u'Future PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })

        connection.execute(contaminated_sites.Geometry.__table__.insert(), {
            'id': '1',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '1',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))'
        })
        connection.execute(contaminated_sites.Geometry.__table__.insert(), {
            'id': '2',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '2',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))'
        })
        connection.execute(contaminated_sites.Geometry.__table__.insert(), {
            'id': '3',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '3',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION('
                    u'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
        })
        connection.execute(contaminated_sites.Geometry.__table__.insert(), {
            'id': '4',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '4',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 2, 2 2, 2 0, 0 0)))'
        })

        connection.close()

    def _import_land_use_plans(self):
        connection = self._engine.connect()

        # Add dummy PLR data for collection geometry test
        wms_url = u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default' \
                  u'&SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png' \
                  u'&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
        connection.execute(land_use_plans.ViewService.__table__.insert(), {
            'id': '1',
            'reference_wms': wms_url.format(self._config.get('srid')),
            'layer_index': 1,
            'layer_opacity': 1.0
        })

        connection.execute(land_use_plans.Office.__table__.insert(), {
            'id': '1',
            'name': {'de': u'Test Office'}
        })

        connection.execute(land_use_plans.DataIntegration.__table__.insert(), {
            'id': '1',
            'date': u'2017-07-01T00:00:00',
            'office_id': '1'
        })

        connection.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
            'id': '1',
            'information': {'de': u'Large polygon PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
            'id': '2',
            'information': {'de': u'Small polygon PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
            'id': '3',
            'information': {'de': u'Double intersection polygon PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })
        connection.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
            'id': '4',
            'information': {'de': u'Future PLR'},
            'topic': u'ContaminatedSites',
            'law_status': u'inForce',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'view_service_id': '1',
            'office_id': '1'
        })

        connection.execute(land_use_plans.Geometry.__table__.insert(), {
            'id': '1',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '1',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION('
                    u'POLYGON((1 -1, 9 -1, 9 7, 1 7, 1 8, 10 8, 10 -2, 1 -2, 1 -1)))'
        })
        connection.execute(land_use_plans.Geometry.__table__.insert(), {
            'id': '2',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '1',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))'
        })
        connection.execute(land_use_plans.Geometry.__table__.insert(), {
            'id': '3',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '1',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION('
                    u'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
        })
        connection.execute(land_use_plans.Geometry.__table__.insert(), {
            'id': '4',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '1',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))'
        })
        connection.execute(land_use_plans.Geometry.__table__.insert(), {
            'id': '5',
            'law_status': u'inForce',
            'published_from': date.today().isoformat(),
            'public_law_restriction_id': '1',
            'office_id': '1',
            'geom': u'SRID=2056;GEOMETRYCOLLECTION(POINT(1 2))'
        })

        connection.close()
