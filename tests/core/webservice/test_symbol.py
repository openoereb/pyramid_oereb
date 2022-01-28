# -*- coding: utf-8 -*-

import pytest
import io
from PIL import Image
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid_oereb.core.records.image import ImageRecord
from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import Symbol


@pytest.fixture
def png_image():
    yield Image.new("RGB", (72, 36), (128, 128, 128))


@pytest.fixture
def png_binary(png_image):
    output = io.BytesIO()
    png_image.save(output, format='PNG')
    yield output.getvalue()


@pytest.fixture
def mock_symbol(png_binary):
    def mock_get_symbol(theme_code, sub_theme_code, view_service_id, type_code, theme_config):
        content_type = ImageRecord.get_mimetype(bytearray(png_binary))
        return png_binary, content_type

    class MockSymbol(Symbol):
        def get_method(self, theme_code):
            return mock_get_symbol
    yield MockSymbol


@pytest.fixture
def mock_symbol_fail():
    class MockSymbol(Symbol):
        def get_method(self, theme_code):
            return None
    yield MockSymbol


def test_get_image(pyramid_oereb_test_config, contaminated_sites, mock_symbol, png_binary):
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ch.BelasteteStandorte',
        'view_service_id': '1',
        'type_code': 'StaoTyp1'
    })
    webservice = mock_symbol(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    assert result.body == png_binary
    assert result.status_int == 200
    assert result.content_type == 'image/png'


def test_get_image_invalid(mock_symbol_fail):
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ch.BelasteteStandorte',
        'view_service_id': '1',
        'type_code': 'notExisting'
    })
    webservice = mock_symbol_fail(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
