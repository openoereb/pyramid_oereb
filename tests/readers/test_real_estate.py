# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.real_estate import RealEstateReader
from shapely.geometry.point import Point


@pytest.mark.run(order=2)
def test_init(config):
    reader = RealEstateReader(
        config.get_real_estate_config().get('source').get('class'),
        **config.get_real_estate_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'nb_ident': 'BLTEST', 'number': '1000'},
    {'egrid': 'TEST'},
    {'geometry': 'SRID=2056;POINT(1 1)'}
])
def test_read(param, config):
    reader = RealEstateReader(
        config.get_real_estate_config().get('source').get('class'),
        **config.get_real_estate_config().get('source').get('params')
    )
    records = reader.read(**param)
    assert len(records) == 1
    record = records[0]
    assert isinstance(record, RealEstateRecord)
    assert record.fosnr == 1234


def test_get_bbox():
    with_bbox = 'https://host/?&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&' \
                'WIDTH=493&HEIGHT=280&FORMAT=image/png'
    p1, p2 = RealEstateReader.get_bbox(with_bbox)
    assert isinstance(p1, Point)
    assert p1.x == 2475000.0
    assert p1.y == 1065000.0
    assert isinstance(p2, Point)
    assert p2.x == 2850000.0
    assert p2.y == 1300000.0

    no_bbox = 'https://host/?&SRS=EPSG:2056WIDTH=493&HEIGHT=280&FORMAT=image/png'
    p3, p4 = RealEstateReader.get_bbox(no_bbox)
    assert p3 is None
    assert p4 is None
