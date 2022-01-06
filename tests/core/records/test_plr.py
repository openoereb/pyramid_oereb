# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
import pytest
from shapely.geometry import Point, LineString, Polygon
from shapely.wkt import loads

from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.plr import PlrRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord, LegendEntryRecord


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


def test_wrong_legend_entry_text_type():
    theme = ThemeRecord('code', dict(), 100)
    plr_record = PlrRecord(
        theme,
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            'legendentry',
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
        [GeometryRecord(law_status, datetime.date.today(), None, Point(1, 1))])
    assert isinstance(plr_record.legend_entry, LegendEntryRecord)


def test_documents_not_none():
    theme = ThemeRecord('code', dict(), 100)
    plr_record = PlrRecord(
        theme,
        LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            'legendentry',
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
