# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
import pytest
from shapely.geometry import Point

from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.plr import PlrRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord, LegendEntryRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        PlrRecord()


def create_dummy_plr():
    office = OfficeRecord({'en': 'Office'})
    view_service = ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None)
    law_status = LawStatusRecord(
        'inKraft', {
            "de": "Rechtskräftig",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force"
        }
    )
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
    law_status = LawStatusRecord(
        'inKraft', {
            "de": "Rechtskräftig",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force"
        }
    )
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
