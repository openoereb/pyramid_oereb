# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch
from datetime import date, timedelta

from pyramid_oereb.core import b64
from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser
from pyramid_oereb.core.config import Config


@pytest.fixture
def file_adapter():
    return FileAdapter()


@pytest.fixture
def wms_url_contaminated_sites():
    return {
        'de': 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=default&'
              'CRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=740&HEIGHT=500&FORMAT=image/png'
              '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
        'fr': 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=default&'
              'CRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=740&HEIGHT=500&FORMAT=image/png'
              '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
            }


@pytest.fixture
def main_schema(pyramid_oereb_test_config, theme_test_data, law_status_test_data,
                document_type_test_data, logo_test_data):

    with patch.object(
      Config, 'themes', theme_test_data
    ), patch.object(
      Config, 'law_status', law_status_test_data
    ), patch.object(
      Config, 'document_types', document_type_test_data
    ), patch.object(
      Config, 'logos', logo_test_data):
        yield pyramid_oereb_test_config


@pytest.fixture
def land_use_plans(pyramid_oereb_test_config, dbsession, transact, wms_url_contaminated_sites, file_adapter):
    del transact

    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.Nutzungsplanung')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    view_services = {
        models.ViewService(**{
            'id': 1,
            'reference_wms': wms_url_contaminated_sites,
            'layer_index': 1,
            'layer_opacity': 1.0,
        })
    }
    dbsession.add_all(view_services)

    offices = {
        models.Office(**{
            'id': 1,
            'name': 'Test office',
        })
    }
    dbsession.add_all(offices)

    legend_entries = {
        models.LegendEntry(**{
            'id': 1,
            'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
            'legend_text': {
                'de': u'Test'
            },
            'type_code': u'CodeA',
            'type_code_list': u'type_code_list',
            'theme': 'ch.Nutzungsplanung',
            'sub_theme': None,
            'view_service_id': 1,
        })
    }
    dbsession.add_all(legend_entries)

    plrs = [
        models.PublicLawRestriction(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        models.PublicLawRestriction(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=00)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        models.PublicLawRestriction(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        models.PublicLawRestriction(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        ]
    dbsession.add_all(plrs)

    geometries = {
        models.Geometry(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Large polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION('
                    'POLYGON((1 -1, 9 -1, 9 7, 1 7, 1 8, 10 8, 10 -2, 1 -2, 1 -1)))',
        }),
        models.Geometry(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Small polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))',
        }),
        models.Geometry(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Double intersection polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION('
                    'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
        }),
        models.Geometry(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Future PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))',
        }),
        models.Geometry(**{
            'id': 5,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Future PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POINT(1 2))',
        }),
    }
    dbsession.add_all(geometries)

    documents = {
        models.Document(**{
            'id': 1,
            'document_type': 'GesetzlicheGrundlage',
            'index': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'title': {'de': 'First level document'},
            'office_id': 1,
            'text_at_web': {'de': 'http://www.admin.ch/ch/d/sr/c814_01.html'},
            'abbreviation': {'de': 'USG', 'fr': 'LPE', 'it': 'LPAmb', 'en': 'EPA'},
            'official_number': {'de': 'SR 814.01'},
        })
    }
    dbsession.add_all(documents)

    plr_documents = {
        models.PublicLawRestrictionDocument(**{
            'id': 1,
            'public_law_restriction_id': 1,
            'document_id': 1,
        })
    }
    dbsession.add_all(plr_documents)
    dbsession.flush()


@pytest.fixture
def contaminated_sites(pyramid_oereb_test_config, dbsession, transact, wms_url_contaminated_sites,
                       file_adapter):
    del transact

    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.BelasteteStandorte')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    view_services = {
        models.ViewService(**{
            'id': 1,
            'reference_wms': wms_url_contaminated_sites,
            'layer_index': 1,
            'layer_opacity': .75,
        })
        }
    dbsession.add_all(view_services)

    offices = {
        'office1': models.Office(**{
            'id': 1,
            'name': 'Test office',
        })
        }
    dbsession.add_all(offices.values())

    legend_entries = {
        'legend_entry1': models.LegendEntry(**{
            'id': 1,
            'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
            'legend_text': 'Test',
            'type_code': 'StaoTyp1',
            'type_code_list': 'https://models.geo.admin.ch/BAFU/KbS_Codetexte_V1_4.xml',
            'theme': 'ch.BelasteteStandorte',
            'view_service_id': 1,
        })
        }
    dbsession.add_all(legend_entries.values())

    plrs = {
        'plr1': models.PublicLawRestriction(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        'plr2': models.PublicLawRestriction(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        'plr3': models.PublicLawRestriction(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        'plr4': models.PublicLawRestriction(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        }
    dbsession.add_all(plrs.values())

    geometries = {
        models.Geometry(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Large polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))',
        }),
        models.Geometry(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Small polygon PLR',
            'public_law_restriction_id': 2,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))',
        }),
        models.Geometry(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Double intersection polygon PLR',
            'public_law_restriction_id': 3,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION('
                    'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
        }),
        models.Geometry(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Future PLR',
            'public_law_restriction_id': 4,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 2, 2 2, 2 0, 0 0)))',
        }),
        }
    dbsession.add_all(geometries)
    dbsession.flush()
