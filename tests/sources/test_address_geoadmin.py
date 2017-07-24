# -*- coding: utf-8 -*-

import sys
import pytest
import requests_mock
from requests import HTTPError

from pyramid_oereb.lib.records.address import AddressRecord
from pyramid_oereb.contrib.sources.address import AddressGeoAdminSource
if sys.version_info.major == 2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode


@pytest.mark.parametrize('i,cfg', [
    (1, {}),
    (2, {'geoadmin_search_api': 'http://my.api.com', 'origins': 'test'}),
    (3, {'geoadmin_search_api': 'http://my.api.com', 'origins': ['test1', 'test2']})
])
def test_init(i, cfg):
    source = AddressGeoAdminSource(**cfg)
    assert isinstance(source, AddressGeoAdminSource)
    if i == 1:
        assert source._geoadmin_url == 'https://api3.geo.admin.ch/rest/services/api/SearchServer'
        assert source._origins == 'address'
    elif i == 2:
        assert source._geoadmin_url == 'http://my.api.com'
        assert source._origins == 'test'
    elif i == 3:
        assert source._geoadmin_url == 'http://my.api.com'
        assert source._origins == 'test1,test2'


@pytest.mark.parametrize('status_code', [200, 400])
def test_read(status_code, config):
    assert isinstance(config._config, dict)
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
    source = AddressGeoAdminSource(geoadmin_search_api=u'http://my.api.com/addresses')
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
                source.read(street_name=street_name, zip_code=zip_code, street_number=street_number)
        else:
            source.read(street_name=street_name, zip_code=zip_code, street_number=street_number)
            assert len(source.records) == 1
            address = source.records[0]
            assert isinstance(address, AddressRecord)
            assert address.street_number == u'36'
            assert address.zip_code == 4410
            assert address.street_name == u'Muehlemattstrasse'
            if sys.version_info.major == 2:
                assert address.geom == 'POINT(2621857.987 1259852.8231)'
            else:
                assert address.geom == 'POINT(2621857.9869956686 1259852.8231037352)'
