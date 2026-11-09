import io
from pyramid_oereb.core.records.extract import ExtractRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
import pytest
import datetime

from shapely.wkt import loads
from unittest.mock import patch
from PIL import Image

from pyramid.testing import DummyRequest

from pyramid_oereb.core import b64
from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import LegendEntryRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.hook_methods import compare, get_symbol, get_symbol_ref, \
    get_logo_ref, get_qr_code_ref, get_surveying_data_update_date, \
    plr_sort_within_themes
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser
from pyramid_oereb.contrib.data_sources import plr_sort_within_themes_by_type_code
import pyramid_oereb.contrib.data_sources.standard.hook_methods
from tests.core.records.test_extract import create_dummy_extract
from tests.core.records.test_plr import create_dummy_plr

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


@pytest.fixture
def legend_entry_data(pyramid_oereb_test_config, dbsession, transact, file_adapter):
    del transact
    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.BelasteteStandorte')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    view_services = {
        models.ViewService(**{
            'id': 1,
            'reference_wms': 'http://www.example.com',
            'layer_index': 1,
            'layer_opacity': 1.0,
        })
    }
    dbsession.add_all(view_services)

    legend_entries = [
        models.LegendEntry(**{
            'id': '1',
            'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
            'legend_text': {'de': 'Test'},
            'type_code': 'CodeA',
            'type_code_list': 'type_code_list',
            'theme': 'ch.BelasteteStandorte',
            'view_service_id': '1'
        })
    ]
    dbsession.add_all(legend_entries)
    dbsession.flush()

    yield legend_entries


@pytest.fixture
def png_image():
    yield Image.new("RGB", (72, 36), (128, 128, 128))


@pytest.fixture
def png_binary(png_image):
    output = io.BytesIO()
    png_image.save(output, format='PNG')
    yield output.getvalue()


def test_get_symbol():
    with pytest.raises(NotImplementedError):
        binary_image, content_type = get_symbol({'identifier': "1"}, {})


@patch.object(pyramid_oereb.core.hook_methods, 'route_prefix', 'oereb')
def test_get_symbol_ref(pyramid_test_config):
    record = LegendEntryRecord(
        ImageRecord(FileAdapter().read('tests/resources/logo_canton.png')),
        {'de': 'Test'},
        'CodeA',
        'http://my.codelist.com/test.xml',
        ThemeRecord('ch.BelasteteStandorte', {'de': 'Belastete Standorte'}, 410),
        view_service_id='1',
        identifier="1"
    )
    request = DummyRequest()
    url = urlparse(get_symbol_ref(request, record))
    assert url.path == '/image/symbol/ch.BelasteteStandorte/legend_entry.png'


@pytest.mark.parametrize('test_value, expected_results', [
    ({
        'logo_code': 'ch',
        'language': 'de',
    }, '/image/logo/ch/de.png'),
    ({
        'logo_code': 'bs',
        'language': 'fr',
    }, '/image/logo/bs/fr.png')
    ])
def test_get_logo_ref(test_value, expected_results, png_binary):
    request = DummyRequest()
    url = urlparse(get_logo_ref(request,
                                test_value.get('logo_code'),
                                test_value.get('language'),
                                {test_value.get('language'): ImageRecord(png_binary)}
                                ))
    assert url.path == expected_results


@pytest.mark.parametrize('test_value, expected_results', [
    ('', ''),
    ({}, {}),
    (None, None)
    ])
def test_get_qr_code_ref(test_value, expected_results):
    request = DummyRequest()
    assert get_qr_code_ref(request, test_value) == expected_results


def test_get_surveying_data_date():
    real_estate = RealEstateRecord('test_type', 'BL', 'Nusshof', 1, 100,
                                   loads('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'))
    update_date_os = get_surveying_data_update_date(real_estate)
    assert isinstance(update_date_os, datetime.datetime)


def test_plr_sort_within_themes():
    record = create_dummy_extract()
    sorted_extract = plr_sort_within_themes(record)
    assert isinstance(sorted_extract, ExtractRecord)


def test_compare():
    assert compare(create_dummy_plr(), create_dummy_plr()) == 0

    plr1 = create_dummy_plr()
    plr1.law_status = LawStatusRecord('AenderungMitVorwirkung', {})
    plr1.theme.code = 'ch.Nutzungsplanung'
    plr1.sub_theme = ''
    plr2 = create_dummy_plr()
    plr2.law_status = LawStatusRecord('inKraft', {})
    plr2.theme.code = 'ch.Nutzungsplanung'
    plr2.sub_theme = ''

    assert compare(plr1, plr2) == 1
    assert compare(plr2, plr1) == -1

    plr1.law_status = LawStatusRecord('inKraft', {})
    assert compare(plr1, plr2) == 0


def test_plr_sort_preserves_theme_order_when_sorting_law_status():
    """
    Regression test for the Basel-Landschaft PLR ordering issue.

    The input is already ordered by theme extract_index.
    Sorting law statuses within a theme must not move a PLR
    ahead of a theme with a lower extract_index.
    """
    extract = create_dummy_extract()

    # Theme 100: Nutzungsplanung
    planning = create_dummy_plr()
    planning.theme = ThemeRecord(
        'ch.Nutzungsplanung',
        {'de': 'Nutzungsplanung'},
        100
    )
    planning.sub_theme = ''
    planning.law_status = LawStatusRecord(
        'AenderungOhneVorwirkung', {}
    )

    # Theme 610: Laermempfindlichkeitsstufen
    noise_change = create_dummy_plr()
    noise_change.theme = ThemeRecord(
        'ch.Laermempfindlichkeitsstufen',
        {'de': 'Lärmempfindlichkeitsstufen'},
        610
    )
    noise_change.sub_theme = ''
    noise_change.law_status = LawStatusRecord(
        'AenderungOhneVorwirkung', {}
    )

    noise_in_force = create_dummy_plr()
    noise_in_force.theme = ThemeRecord(
        'ch.Laermempfindlichkeitsstufen',
        {'de': 'Lärmempfindlichkeitsstufen'},
        610
    )
    noise_in_force.sub_theme = ''
    noise_in_force.law_status = LawStatusRecord(
        'inKraft', {}
    )

    # Correct theme order, incorrect order within theme 610.
    extract.real_estate.public_law_restrictions = [
        planning,
        noise_change,
        noise_in_force,
    ]

    result = plr_sort_within_themes(extract)

    # The planning restriction must remain first.
    # Within theme 610, inKraft must precede
    # AenderungOhneVorwirkung.
    assert result.real_estate.public_law_restrictions == [
        planning,
        noise_in_force,
        noise_change,
    ]


def test_plr_sort_preserves_theme_order_when_sorting_type_code():
    """
    Regression test for PLR sorting by type code.

    Preserve the extract_index theme order while sorting
    type codes within each theme.
    """
    extract = create_dummy_extract()

    planning = create_dummy_plr()
    planning.theme = ThemeRecord(
        'ch.Nutzungsplanung',
        {'de': 'Nutzungsplanung'},
        100
    )
    planning.sub_theme = ''
    planning.type_code = 'B'

    noise_b = create_dummy_plr()
    noise_b.theme = ThemeRecord(
        'ch.Laermempfindlichkeitsstufen',
        {'de': 'Lärmempfindlichkeitsstufen'},
        610
    )
    noise_b.sub_theme = ''
    noise_b.type_code = 'B'

    noise_a = create_dummy_plr()
    noise_a.theme = ThemeRecord(
        'ch.Laermempfindlichkeitsstufen',
        {'de': 'Lärmempfindlichkeitsstufen'},
        610
    )
    noise_a.sub_theme = ''
    noise_a.type_code = 'A'

    # Correct theme order, incorrect type-code order.
    extract.real_estate.public_law_restrictions = [
        planning,
        noise_b,
        noise_a,
    ]

    result = plr_sort_within_themes_by_type_code(extract)

    assert result.real_estate.public_law_restrictions == [
        planning,
        noise_a,
        noise_b,
    ]
