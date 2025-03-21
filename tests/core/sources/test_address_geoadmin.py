# -*- coding: utf-8 -*-

from pyramid_oereb.core.records.address import AddressRecord
from pyramid_oereb.contrib.data_sources.swisstopo.address import AddressGeoAdminSource
import sys
import pytest
import requests_mock
from requests import HTTPError
from shapely.geometry import Point
from tests.mockrequest import MockParameter
from urllib.parse import urlencode


@pytest.mark.parametrize('i, cfg', [
    (1, {}),
    (2, {'referer': 'http://ref.ch', 'geoadmin_search_api': 'http://my.api.com', 'origins': 'test'}),
    (3, {'referer': 'http://ref.ch', 'geoadmin_search_api': 'http://my.api.com',
         'origins': ['test1', 'test2']})
])
def test_init(i, cfg):
    source = AddressGeoAdminSource(**cfg)
    assert isinstance(source, AddressGeoAdminSource)
    if i == 1:
        assert source._referer is None
        assert source._geoadmin_url == 'https://api3.geo.admin.ch/rest/services/api/SearchServer'
        assert source._origins == 'address'
    elif i == 2:
        assert source._referer == 'http://ref.ch'
        assert source._geoadmin_url == 'http://my.api.com'
        assert source._origins == 'test'
    elif i == 3:
        assert source._referer == 'http://ref.ch'
        assert source._geoadmin_url == 'http://my.api.com'
        assert source._origins == 'test1,test2'


@pytest.mark.parametrize('status_code', [200, 400])
def test_read(pyramid_oereb_test_config, status_code):
    response = {
        'results': [
            {
                'id': 702086,
                'weight': 4,
                'attrs': {
                    'origin': 'address',
                    'geom_quadindex': '021101213123030020322',
                    'layerBodId': 'ch.bfs.gebaeude_wohnungs_register',
                    'zoomlevel': 10,
                    'featureId': '2355731_0',
                    'lon': 7.728659152984619,
                    'detail': 'muehlemattstrasse 36 4410 liestal 2829 liestal ch bl',
                    'rank': 7,
                    'geom_st_box2d': 'BOX(621857.447 259852.534,621857.447 259852.534)',
                    'lat': 47.48907470703125,
                    'num': 36,
                    'y': 621857.4375,
                    'x': 259852.53125,
                    'label': 'Muehlemattstrasse 36 <b>4410 Liestal</b>'
                }
            }
        ]
    }
    source = AddressGeoAdminSource(
            geoadmin_search_api=u'http://my.api.com/addresses')
    zip_code = 4410
    street_name = u'Muehlemattstrasse'
    street_number = u'36'
    url = u'http://my.api.com/addresses?' + urlencode({
        'searchText': u'{0} {1} {2}'.format(zip_code, street_name, street_number),
        'type': source._type,
        'origins': source._origins
    })
    with requests_mock.mock() as m:
        m.get(url, json=response, status_code=status_code)
        if status_code == 400:
            with pytest.raises(HTTPError):
                source.read(MockParameter(), street_name=street_name, zip_code=zip_code,
                            street_number=street_number)
        else:
            source.read(MockParameter(), street_name=street_name, zip_code=zip_code,
                        street_number=street_number)
            assert len(source.records) == 1
            address = source.records[0]
            assert isinstance(address, AddressRecord)
            assert address.street_number == u'36'
            assert address.zip_code == 4410
            assert address.street_name == u'Muehlemattstrasse'
            assert isinstance(address.geom, Point)
            assert address.geom.x == 2621857.986995669

            # TODO: Remove workaround when Python 3.9 will no longer be supported
            # This is a workaround needed as long as Python 3.9 is supported due to Numpy v2.2.4 used in
            # Python 3.10 or higher, which does not support Python versions 3.9 or lower
            # (where Numpy v2.0.2 or lower is used)
            # Define the expected y-coordinate value based on Python version
            if sys.version_info[:2] > (3, 9):
                expected_geom_y = 1259852.8231037296
            else:
                expected_geom_y = 1259852.8231037268

            assert address.geom.y == expected_geom_y
