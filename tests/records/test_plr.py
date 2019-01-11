# -*- coding: utf-8 -*-
import datetime
import pytest
from shapely.geometry import Point

from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        PlrRecord()


def test_init():
    office = OfficeRecord({'en': 'Office'})
    view_service = ViewServiceRecord('http://my.wms.com', 1, 1.0)
    law_status = LawStatusRecord.from_config(u'inForce')
    geometry = GeometryRecord(law_status, datetime.date.today(), Point(1, 1))
    record = PlrRecord(
        ThemeRecord('code', dict()), {'en': 'Content'}, law_status, datetime.date(1985, 8, 29), office,
        ImageRecord('1'.encode('utf-8')), view_service, [geometry])
    assert record.information == {'en': 'Content'}
    assert record.sub_theme is None
    assert isinstance(record.geometries, list)
    assert isinstance(record.responsible_office, OfficeRecord)
    assert isinstance(record.theme, ThemeRecord)
    assert isinstance(record.symbol, ImageRecord)
