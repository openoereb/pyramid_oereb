# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
from sys import float_info as fi
import pytest
from unittest.mock import patch
from shapely.geometry import Point, LineString, Polygon, GeometryCollection
from shapely.wkt import loads

from pyramid_oereb.core.processor import create_processor
from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.municipality import MunicipalityRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.plr import PlrRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord, LegendEntryRecord
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser


law_status = LawStatusRecord(
    'inKraft', {
        "de": "Rechtskräftig",
        "fr": "En vigueur",
        "it": "In vigore",
        "rm": "En vigur",
        "en": "In force"
    }
)


def test_mandatory_fields():
    with pytest.raises(TypeError):
        PlrRecord()


def create_dummy_plr():
    office = OfficeRecord({'en': 'Office'})
    view_service = ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None)
    geometry = GeometryRecord(law_status, datetime.date.today(), None, Point(1, 1))
    record = PlrRecord(
        ThemeRecord('code', dict(), 100),
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            {'en': 'Content'},
            'CodeA',
            None,
            ThemeRecord('code', dict(), 100),
            view_service_id=1
        ),
        law_status,
        datetime.date(1985, 8, 29),
        None,
        office,
        ImageRecord('1'.encode('utf-8')), view_service, [geometry])
    return record


def test_init():
    record = create_dummy_plr()
    assert record.legend_text == {'en': 'Content'}
    assert record.sub_theme is None
    assert isinstance(record.geometries, list)
    assert isinstance(record.responsible_office, OfficeRecord)
    assert isinstance(record.theme, ThemeRecord)
    assert isinstance(record.symbol, ImageRecord)


@pytest.mark.parametrize('published_from,published_until,published', [
    (date.today() + timedelta(days=0), date.today() + timedelta(days=2), True),
    (date.today() + timedelta(days=1), date.today() + timedelta(days=2), False),
    (date.today() - timedelta(days=3), date.today() - timedelta(days=2), False),
    (date.today() + timedelta(days=0), None, True),
    (date.today() + timedelta(days=1), None, False)]
)
def test_published(published_from, published_until, published):
    theme = ThemeRecord('code', dict(), 100)
    plr_record = PlrRecord(
        theme,
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            {'en': 'Content'},
            'CodeA',
            None,
            theme,
            view_service_id=1
        ),
        law_status,
        published_from,
        published_until,
        OfficeRecord({'en': 'Office'}),
        ImageRecord('1'.encode('utf-8')),
        ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None),
        [GeometryRecord(law_status, datetime.date.today(), None, Point(1, 1))])
    assert plr_record.published == published


@pytest.mark.filterwarnings("ignore: Type of")
def test_wrong_legend_entry_text_type():
    theme = ThemeRecord('code', dict(), 100)
    with pytest.warns(UserWarning):
        legendentry = LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            'legendentry_intentional_wrong_structure',
            'CodeA',
            None,
            theme,
            view_service_id=1
        )
    plr_record = PlrRecord(
        theme,
        legendentry,
        law_status,
        date.today() + timedelta(days=0),
        date.today() + timedelta(days=2),
        OfficeRecord({'en': 'Office'}),
        ImageRecord('1'.encode('utf-8')),
        ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None),
        [GeometryRecord(law_status, datetime.date.today(), None, Point(1, 1))])
    assert isinstance(plr_record.legend_entry, LegendEntryRecord)


def test_documents_not_none():
    theme = ThemeRecord('code', dict(), 100)
    plr_record = PlrRecord(
        theme,
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            {'en': 'Content'},
            'CodeA',
            None,
            theme,
            view_service_id=1
        ),
        law_status,
        date.today() + timedelta(days=0),
        date.today() + timedelta(days=2),
        OfficeRecord({'en': 'Office'}),
        ImageRecord('1'.encode('utf-8')),
        ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None),
        [GeometryRecord(law_status, datetime.date.today(), None, Point(1, 1))],
        documents=[]
    )
    assert isinstance(plr_record.documents, list)


def test_serialization():
    theme = ThemeRecord('code', dict(), 100)
    plr_record = PlrRecord(
        theme,
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            {'en': 'Content'},
            'CodeA',
            None,
            theme,
            view_service_id=1
        ),
        law_status,
        date.today() + timedelta(days=0),
        date.today() + timedelta(days=2),
        OfficeRecord({'en': 'Office'}),
        ImageRecord('1'.encode('utf-8')),
        ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None),
        [GeometryRecord(law_status, datetime.date.today(), None, Point(1, 1))],
        documents=[]
    )
    assert isinstance(str(plr_record), str)


@pytest.mark.parametrize(
    'geometry_record,test,method', [
        (GeometryRecord(law_status, datetime.date.today(), None, Point(0.5, 0.5)), 1, '_sum_points'),  # noqa: E501
        (GeometryRecord(law_status, datetime.date.today(), None, LineString([(0, 0), (0, 1)])), 1, '_sum_length'),  # noqa: E501
        (GeometryRecord(law_status, datetime.date.today(), None, Polygon([(0, 0), (1, 1), (1, 0)])), 0.5, '_sum_area')  # noqa: E501
    ]
)
def test_sum_points(geometry_record, test, method, geometry_types):

    theme = ThemeRecord('code', dict(), 100)
    real_estate_record = RealEstateRecord(
        'test_type', 'BL', 'Nusshof', 1, 100,
        loads('POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))')
    )
    geometry_record.calculate(real_estate_record, 0.1, 0.1, 'm', 'm2', geometry_types)
    plr_record = PlrRecord(
        theme,
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            {'en': 'Content'},
            'CodeA',
            None,
            theme,
            view_service_id=1
        ),
        law_status,
        date.today() + timedelta(days=0),
        date.today() + timedelta(days=2),
        OfficeRecord({'en': 'Office'}),
        ImageRecord('1'.encode('utf-8')),
        ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None),
        [geometry_record],
        documents=[]
    )
    assert getattr(plr_record, method)() == test


@pytest.fixture
def oblique_geometry_plr_record():
    theme = ThemeRecord('code', dict(), 100)
    geometry_records = [
        GeometryRecord(law_status, datetime.date.today(), None, LineString(((1, 0.1), (2, 0.2))))
    ]
    return PlrRecord(
        theme,
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            {'en': 'Content'},
            'CodeA',
            None,
            theme,
            view_service_id=1
        ),
        law_status,
        date.today() + timedelta(days=0),
        date.today() + timedelta(days=2),
        OfficeRecord({'en': 'Office'}),
        ImageRecord('1'.encode('utf-8')),
        ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None),
        geometry_records,
        documents=[]
    )


@pytest.fixture
def oblique_limit_real_estate_record():
    return RealEstateRecord(
        'test_type', 'BL', 'Nusshof', 1234, land_registry_area=3.2,
        limit=Polygon(((0, 0), (3, 0), (3, 0.3)))
    )


def test_tolerance_outside(geometry_types, oblique_geometry_plr_record, oblique_limit_real_estate_record):
    oblique_geometry_plr_record.geometries[0].reset_calculation()
    assert not oblique_geometry_plr_record.geometries[0].calculate(
        oblique_limit_real_estate_record,
        oblique_geometry_plr_record.min_length, oblique_geometry_plr_record.min_area,
        oblique_geometry_plr_record.length_unit, oblique_geometry_plr_record.area_unit,
        geometry_types
    )


def test_tolerance_inside(geometry_types, oblique_geometry_plr_record, oblique_limit_real_estate_record):
    oblique_geometry_plr_record.geometries[0].reset_calculation()
    assert oblique_geometry_plr_record.geometries[0].calculate(
        oblique_limit_real_estate_record,
        oblique_geometry_plr_record.min_length, oblique_geometry_plr_record.min_area,
        oblique_geometry_plr_record.length_unit, oblique_geometry_plr_record.area_unit,
        geometry_types, tolerances={'ALL': fi.epsilon}
    )


@pytest.fixture
def processor_data(pyramid_oereb_test_config, main_schema):
    with patch(
        'pyramid_oereb.core.config.Config.municipalities',
        [MunicipalityRecord(1234, 'test', True)]
    ):
        yield pyramid_oereb_test_config


def test_linestring_calculation(geometry_types,
                                oblique_geometry_plr_record,
                                oblique_limit_real_estate_record):
    oblique_geometry_plr_record.tolerances = {'ALL': fi.epsilon}
    oblique_geometry_plr_record.calculate(oblique_limit_real_estate_record, geometry_types)
    assert oblique_geometry_plr_record.length_share > 0


@pytest.fixture(params=['SRID=2056;GEOMETRYCOLLECTION(LINESTRING (1 0.1, 2 0.2))'])
def oblique_land_use_plan(request, pyramid_oereb_test_config, dbsession, transact, land_use_plans):
    del transact

    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.Nutzungsplanung')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    dbsession.add(models.PublicLawRestriction(id=5, law_status='inKraft',
                                              published_from=(date.today() - timedelta(days=7)).isoformat(),
                                              published_until=(date.today() + timedelta(days=7)).isoformat(),
                                              view_service_id=1,
                                              legend_entry_id=1, office_id=1))
    dbsession.add(models.Geometry(id=6, law_status='inKraft', public_law_restriction_id=5,
                                  published_from=(date.today() - timedelta(days=7)).isoformat(),
                                  published_until=(date.today() + timedelta(days=100)).isoformat(),
                                  geom=request.param))
    dbsession.flush()


def test_linestring_process_no_tol(real_estate_data, main_schema, land_use_plans, processor_data,
                                   oblique_land_use_plan, oblique_limit_real_estate_record):
    from pyramid_oereb.core.views.webservice import Parameter
    from pyramid_oereb.core.config import Config

    processor = create_processor()
    request_params = Parameter('json', egrid='TEST')

    municipality = Config.municipality_by_fosnr(oblique_limit_real_estate_record.fosnr)
    extract_raw = processor._extract_reader_.read(
        request_params, oblique_limit_real_estate_record, municipality
    )
    extract = processor.plr_tolerance_check(extract_raw)
    plrs = extract.real_estate.public_law_restrictions
    assert len(plrs) == 0


def test_linestring_process_with_tol(real_estate_data, main_schema, land_use_plans, processor_data,
                                     oblique_land_use_plan, oblique_limit_real_estate_record):
    from pyramid_oereb.core.views.webservice import Parameter
    from pyramid_oereb.core.config import Config

    for i, plr in enumerate(Config._config["plrs"]):
        Config._config["plrs"][i]["tolerances"] = {'ALL': fi.epsilon}

    processor = create_processor()
    request_params = Parameter('json', egrid='TEST')

    municipality = Config.municipality_by_fosnr(oblique_limit_real_estate_record.fosnr)
    extract_raw = processor._extract_reader_.read(
        request_params, oblique_limit_real_estate_record, municipality
    )
    extract = processor.plr_tolerance_check(extract_raw)
    plrs = extract.real_estate.public_law_restrictions
    assert len(plrs) == 1
    assert plrs[0].length_share == 1


@pytest.fixture
def oblique_limit_collection_real_estate_record():
    return RealEstateRecord(
        'test_type', 'BL', 'Nusshof', 1234, land_registry_area=3.2,
        limit=GeometryCollection([Polygon(((0, 0), (3, 0), (3, 0.3)))])
    )


def test_linestring_collection_process(real_estate_data, main_schema, land_use_plans, processor_data,
                                       oblique_land_use_plan, oblique_limit_collection_real_estate_record):
    from pyramid_oereb.core.views.webservice import Parameter
    from pyramid_oereb.core.config import Config

    for i, plr in enumerate(Config._config["plrs"]):
        Config._config["plrs"][i]["tolerances"] = {'ALL': fi.epsilon}
        Config._config["plrs"][i]["geometry_type"] = "GEOMETRYCOLLECTION"

    processor = create_processor()
    request_params = Parameter('json', egrid='TEST')

    municipality = Config.municipality_by_fosnr(oblique_limit_collection_real_estate_record.fosnr)
    extract_raw = processor._extract_reader_.read(
        request_params, oblique_limit_collection_real_estate_record, municipality
    )
    extract = processor.plr_tolerance_check(extract_raw)
    plrs = extract.real_estate.public_law_restrictions
    assert len(plrs) == 1
    assert plrs[0].length_share == 1
