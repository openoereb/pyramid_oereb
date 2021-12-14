import pytest
from unittest.mock import patch
from pyramid_oereb.core import b64
from pyramid_oereb.core.adapter import FileAdapter

from datetime import date, timedelta

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.logo import LogoRecord
from pyramid_oereb.core.records.real_estate_type import RealEstateTypeRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord


file_adapter = FileAdapter()


@pytest.fixture
def municipalities(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models import main

    # Add dummy municipality
    municipalities = [main.Municipality(**{
        'fosnr': 1234,
        'name': u'Test',
        'published': True,
        'geom': 'SRID=2056;MULTIPOLYGON(((0 0, 0 10, 10 10, 10 0, 0 0)))'
    })]
    dbsession.add_all(municipalities)


@pytest.fixture
def real_estate(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models import main

    real_estates = [main.RealEstate(**{
        'id': '1',
        'egrid': u'TEST',
        'number': u'1000',
        'identdn': u'BLTEST',
        'type': u'Liegenschaft',
        'canton': u'BL',
        'municipality': u'Liestal',
        'fosnr': 1234,
        'land_registry_area': 4,
        'limit': 'SRID=2056;MULTIPOLYGON(((0 0, 0 2, 2 2, 2 0, 0 0)))'
    }), main.RealEstate(**{
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
    })]
    dbsession.add_all(real_estates)


@pytest.fixture
def address(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models import main

    # Add dummy address
    addresses = [main.Address(**{
        'street_name': u'test',
        'street_number': u'10',
        'zip_code': 4410,
        'geom': 'SRID=2056;POINT(1 1)'
    })]
    dbsession.add_all(addresses)


@pytest.fixture
def real_estate_types_test_data(pyramid_oereb_test_config):
    with patch.object(Config, 'real_estate_types', [RealEstateTypeRecord(
            'Liegenschaft',
            {
                "de": "Liegenschaft",
                "fr": "Bien-fonds",
                "it": "Bene immobile",
                "rm": "Bain immobigliar",
                "en": "Property"
            }
    )]):
        yield pyramid_oereb_test_config


@pytest.fixture
def logos(pyramid_oereb_test_config):
    with patch.object(Config, 'logos', [
            LogoRecord('ch', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ch.plr', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ne', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ch.1234', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
    ]):
        yield pyramid_oereb_test_config


@pytest.fixture
def themes(pyramid_oereb_test_config):
    with patch.object(Config, 'themes', [
            ThemeRecord(**{
                'code': 'ch.Nutzungsplanung',
                'sub_code': None,
                'title': {"de": "Nutzungsplanung (kantonal/kommunal)",
                          "fr": "Plans d’affectation (cantonaux/communaux)",
                          "it": "Piani di utilizzazione (cantonali/comunali)",
                          "rm": "Planisaziun d''utilisaziun (chantunal/communal)",
                          "en": "Land use plans (cantonal/municipal)"},
                'extract_index': 20
            }),
            ThemeRecord(**{
                'code': 'ch.StatischeWaldgrenzen',
                'title': {"de": "Statische Waldgrenzen",
                          "fr": "Limites forestières statiques",
                          "it": "Margini statici della foresta",
                          "rm": "Cunfins statics dal guaud",
                          "en": "Static forest perimeters"},
                'extract_index': 710
            }),
            ThemeRecord(**{
                'code': 'ch.ProjektierungszonenNationalstrassen',
                'title': {"de": "Projektierungszonen Nationalstrassen",
                          "fr": "Zones réservées des routes nationales",
                          "it": "Zone riservate per le strade nazionali",
                          "rm": "Zonas da projectaziun da las vias naziunalas",
                          "en": "Reserved zones for motorways"},
                'extract_index': 110
            }),
            ThemeRecord(**{
                'code': 'ch.BelasteteStandorte',
                'title': {"de": "Kataster der belasteten Standorte",
                          "fr": "Cadastre des sites pollués",
                          "it": "Catasto dei siti inquinati",
                          "rm": "Cataster dals lieus contaminads",
                          "en": "Cadastre of contaminated sites"},
                'extract_index': 410
            }),
    ]):
        yield pyramid_oereb_test_config

    # del transact

    # from pyramid_oereb.contrib.data_sources.standard.models import main
    # # theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.Nutzungsplanung')
    # # config_parser = StandardThemeConfigParser(**theme_config)
    # # models = config_parser.get_models()

    # # Add dummy municipality
    # themes = [main.Theme(**{
    #     'id': 'ch.Nutzungsplanung',
    #     'code': 'ch.Nutzungsplanung',
    #     'sub_code': None,
    #     'title': {"de": "Nutzungsplanung (kantonal/kommunal)",
    #               "fr": "Plans d’affectation (cantonaux/communaux)",
    #               "it": "Piani di utilizzazione (cantonali/comunali)",
    #               "rm": "Planisaziun d''utilisaziun (chantunal/communal)",
    #               "en": "Land use plans (cantonal/municipal)"},
    #     'extract_index': 20
    # })]
    # dbsession.add_all(themes)


@pytest.fixture
def law_test_data(pyramid_oereb_test_config):
    with patch.object(Config, 'law_status', [LawStatusRecord(
            'inKraft',
            {
                "de": "Rechtskräftig",
                "fr": "En vigueur",
                "it": "In vigore",
                "rm": "En vigur",
                "en": "In force"
            }
    )]):
        yield pyramid_oereb_test_config


# @pytest.fixture
# def motorways_building_lines_plrs(dbsession, transact):
#         from pyramid_oereb.contrib.data_sources.standard.models import motorways_building_lines

#         # Add dummy PLR data for line geometry
#         wms_url = u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default' \
#                   u'&SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png' \
#                   u'&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
#         dbsession.execute(motorways_building_lines.ViewService.__table__.insert(), {
#             'id': '1',
#             'reference_wms': wms_url.format(Config.get('srid')),
#             'layer_index': 1,
#             'layer_opacity': 1.0
#         })
#         dbsession.execute(motorways_building_lines.LegendEntry.__table__.insert(), {
#             'id': '1',
#             'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
#             'legend_text': {
#                 'de': u'Test'
#             },
#             'type_code': u'CodeA',
#             'type_code_list': u'type_code_list',
#             'topic': u'MotorwaysBuildingLines',
#             'view_service_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.Office.__table__.insert(), {
#             'id': '1',
#             'name': {'de': u'Test Office'}
#         })
#         dbsession.execute(motorways_building_lines.DataIntegration.__table__.insert(), {
#             'id': '1',
#             'date': u'2017-07-01T00:00:00',
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
#             'id': '1',
#             'information': {'de': u'Long line PLR'},
#             'topic': u'MotorwaysBuildingLines',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
#             'id': '2',
#             'information': {'de': u'Short line PLR'},
#             'topic': u'MotorwaysBuildingLines',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
#             'id': '3',
#             'information': {'de': u'Double intersection line PLR'},
#             'topic': u'MotorwaysBuildingLines',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.PublicLawRestriction.__table__.insert(), {
#             'id': '4',
#             'information': {'de': u'Future geometry'},
#             'topic': u'MotorwaysBuildingLines',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.Geometry.__table__.insert(), {
#             'id': '1',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '1',
#             'office_id': '1',
#             'geom': u'SRID=2056;LINESTRING (0 0, 2 2)'
#         })
#         dbsession.execute(motorways_building_lines.Geometry.__table__.insert(), {
#             'id': '2',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '2',
#             'office_id': '1',
#             'geom': u'SRID=2056;LINESTRING (1.5 1.5, 1.5 2.5)'
#         })
#         dbsession.execute(motorways_building_lines.Geometry.__table__.insert(), {
#             'id': '3',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '3',
#             'office_id': '1',
#             'geom': u'SRID=2056;LINESTRING (3 1, 3 4, 6 4, 6 1, 4.5 1)'
#         })
#         dbsession.execute(motorways_building_lines.Geometry.__table__.insert(), {
#             'id': '4',
#             'law_status': u'inForce',
#             'published_from': (date.today() + timedelta(days=7)).isoformat(),
#             'public_law_restriction_id': '4',
#             'office_id': '1',
#             'geom': u'SRID=2056;LINESTRING (0 0, 4 4)'
#         })
#         dbsession.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
#             'id': '1',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'type': u'document'
#         })
#         dbsession.execute(motorways_building_lines.Document.__table__.insert(), {
#             'id': '1',
#             'document_type': u'Law',
#             'title': {'de': u'First level document'},
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
#             'id': '2',
#             'law_status': u'inForce',
#             'published_from': (date.today() + timedelta(days=7)).isoformat(),
#             'type': u'document'
#         })
#         dbsession.execute(motorways_building_lines.Document.__table__.insert(), {
#             'id': '2',
#             'document_type': u'Law',
#             'title': {'de': u'First level future document'},
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
#             'id': '3',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'type': u'document'
#         })
#         dbsession.execute(motorways_building_lines.Document.__table__.insert(), {
#             'id': '3',
#             'document_type': u'Law',
#             'title': {'de': u'Second level document'},
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.DocumentBase.__table__.insert(), {
#             'id': '4',
#             'law_status': u'inForce',
#             'published_from': (date.today() + timedelta(days=7)).isoformat(),
#             'type': u'document'
#         })
#         dbsession.execute(motorways_building_lines.Document.__table__.insert(), {
#             'id': '4',
#             'document_type': u'Law',
#             'title': {'de': u'Second level future document'},
#             'office_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.PublicLawRestrictionDocument.__table__.insert(), {
#             'id': '1',
#             'public_law_restriction_id': '1',
#             'document_id': '1'
#         })
#         dbsession.execute(motorways_building_lines.PublicLawRestrictionDocument.__table__.insert(), {
#             'id': '2',
#             'public_law_restriction_id': '1',
#             'document_id': '2'
#         })
#         dbsession.execute(motorways_building_lines.DocumentReference.__table__.insert(), {
#             'id': '1',
#             'document_id': '1',
#             'reference_document_id': '3'
#         })
#         dbsession.execute(motorways_building_lines.DocumentReference.__table__.insert(), {
#             'id': '2',
#             'document_id': '1',
#             'reference_document_id': '4'
#         })


# @pytest.fixture
# def contaminated_sites_plrs(dbsession, transact):
#         from pyramid_oereb.contrib.data_sources.standard.models import contaminated_sites

#         theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.BelasteteStandorte')
#         config_parser = StandardThemeConfigParser(**theme_config)
#         models = config_parser.get_models()

#         # Add dummy PLR data for polygon geometry
#         wms_url = u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default' \
#                   u'&SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png' \
#                   u'&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
#         dbsession.execute(models.ViewService.__table__.insert(), {
#             'id': '1',
#             'reference_wms': wms_url.format(Config.get('srid')),
#             'layer_index': 1,
#             'layer_opacity': 1.0
#         })

#         dbsession.execute(models.LegendEntry.__table__.insert(), {
#             'id': '1',
#             'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
#             'legend_text': {
#                 'de': u'Test'
#             },
#             'type_code': u'CodeA',
#             'type_code_list': u'type_code_list',
#             'topic': u'ContaminatedSites',
#             'view_service_id': '1'
#         })

#         dbsession.execute(models.Office.__table__.insert(), {
#             'id': '1',
#             'name': {'de': u'Test Office'}
#         })

#         dbsession.execute(models.DataIntegration.__table__.insert(), {
#             'id': '1',
#             'date': u'2017-07-01T00:00:00',
#             'office_id': '1'
#         })

#         dbsession.execute(models.PublicLawRestriction.__table__.insert(), {
#             'id': '1',
#             'information': {'de': u'Large polygon PLR'},
#             'topic': u'ContaminatedSites',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(models.PublicLawRestriction.__table__.insert(), {
#             'id': '2',
#             'information': {'de': u'Small polygon PLR'},
#             'topic': u'ContaminatedSites',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(models.PublicLawRestriction.__table__.insert(), {
#             'id': '3',
#             'information': {'de': u'Double intersection polygon PLR'},
#             'topic': u'ContaminatedSites',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(models.PublicLawRestriction.__table__.insert(), {
#             'id': '4',
#             'information': {'de': u'Future PLR'},
#             'topic': u'ContaminatedSites',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': (date.today() + timedelta(days=7)).isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })

#         dbsession.execute(models.Geometry.__table__.insert(), {
#             'id': '1',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '1',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))'
#         })
#         dbsession.execute(models.Geometry.__table__.insert(), {
#             'id': '2',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '2',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))'
#         })
#         dbsession.execute(models.Geometry.__table__.insert(), {
#             'id': '3',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '3',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION('
#                     u'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
#         })
#         dbsession.execute(models.Geometry.__table__.insert(), {
#             'id': '4',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '4',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 2, 2 2, 2 0, 0 0)))'
#         })


# @pytest.fixture
# def land_use_plans_plrs(dbsession, transact):
#         from pyramid_oereb.contrib.data_sources.standard.models import land_use_plans

#         # Add dummy PLR data for collection geometry test
#         wms_url = u'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default' \
#                   u'&SRS=EPSG:{0}&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png' \
#                   u'&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
#         dbsession.execute(land_use_plans.ViewService.__table__.insert(), {
#             'id': '1',
#             'reference_wms': wms_url.format(Config.get('srid')),
#             'layer_index': 1,
#             'layer_opacity': 1.0
#         })

#         dbsession.execute(land_use_plans.LegendEntry.__table__.insert(), {
#             'id': '1',
#             'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
#             'legend_text': {
#                 'de': u'Test'
#             },
#             'type_code': u'CodeA',
#             'type_code_list': u'type_code_list',
#             'topic': u'LandUsePlans',
#             'view_service_id': '1'
#         })

#         dbsession.execute(land_use_plans.Office.__table__.insert(), {
#             'id': '1',
#             'name': {'de': u'Test Office'}
#         })

#         dbsession.execute(land_use_plans.DataIntegration.__table__.insert(), {
#             'id': '1',
#             'date': u'2017-07-01T00:00:00',
#             'office_id': '1'
#         })

#         dbsession.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
#             'id': '1',
#             'information': {'de': u'Large polygon PLR'},
#             'topic': u'LandUsePlans',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
#             'id': '2',
#             'information': {'de': u'Small polygon PLR'},
#             'topic': u'LandUsePlans',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
#             'id': '3',
#             'information': {'de': u'Double intersection polygon PLR'},
#             'topic': u'LandUsePlans',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })
#         dbsession.execute(land_use_plans.PublicLawRestriction.__table__.insert(), {
#             'id': '4',
#             'information': {'de': u'Future PLR'},
#             'topic': u'LandUsePlans',
#             'type_code': u'CodeA',
#             "type_code_list": u'',
#             'law_status': u'inForce',
#             'published_from': (date.today() + timedelta(days=7)).isoformat(),
#             'view_service_id': '1',
#             'office_id': '1'
#         })

#         dbsession.execute(land_use_plans.Geometry.__table__.insert(), {
#             'id': '1',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '1',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION('
#                     u'POLYGON((1 -1, 9 -1, 9 7, 1 7, 1 8, 10 8, 10 -2, 1 -2, 1 -1)))'
#         })
#         dbsession.execute(land_use_plans.Geometry.__table__.insert(), {
#             'id': '2',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '1',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))'
#         })
#         dbsession.execute(land_use_plans.Geometry.__table__.insert(), {
#             'id': '3',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '1',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION('
#                     u'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
#         })
#         dbsession.execute(land_use_plans.Geometry.__table__.insert(), {
#             'id': '4',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '1',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))'
#         })
#         dbsession.execute(land_use_plans.Geometry.__table__.insert(), {
#             'id': '5',
#             'law_status': u'inForce',
#             'published_from': date.today().isoformat(),
#             'public_law_restriction_id': '1',
#             'office_id': '1',
#             'geom': u'SRID=2056;GEOMETRYCOLLECTION(POINT(1 2))'
#         })
