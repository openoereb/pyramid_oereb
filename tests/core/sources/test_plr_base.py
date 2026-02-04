# -*- coding: utf-8 -*-
import pytest
from shapely.geometry.base import BaseGeometry

from pyramid_oereb.core.sources.plr import PlrBaseSource

@pytest.fixture
def real_estate_data():
    from pyramid_oereb.contrib.data_sources.standard.models.main import RealEstate
    real_estates = [
        RealEstate(**{
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
    ]
    yield real_estates

def test_read(real_estate_data):
    from pyramid_oereb.core.views.webservice import Parameter
    parameter = Parameter(response_format='application/json')
    source = PlrBaseSource()
    geometry = BaseGeometry()
    assert source.read(parameter, real_estate_data, geometry) == []

def test_info():
    source = PlrBaseSource(name='test')
    assert source.info == {'name': 'test'}
