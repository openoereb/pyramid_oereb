# -*- coding: utf-8 -*-

import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from pyramid_oereb.core.adapter import FileAdapter
from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import Symbol
from tests.core.readers.conftest import contaminated_sites, wms_url_contaminated_sites, file_adapter  # noqa. F401


def test_get_image(pyramid_oereb_test_config, contaminated_sites):  # noqa. F811
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ch.BelasteteStandorte',
        'view_service_id': '1',
        'type_code': 'StaoTyp1'
    })
    webservice = Symbol(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    assert result.body == FileAdapter().read('tests/resources/symbol.png')


def test_get_image_invalid():
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ch.BelasteteStandorte',
        'view_service_id': '1',
        'type_code': 'notExisting'
    })
    webservice = Symbol(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
