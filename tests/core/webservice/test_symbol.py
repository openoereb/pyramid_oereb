# -*- coding: utf-8 -*-

import pytest
import io
from PIL import Image
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid_oereb.core.records.image import ImageRecord
from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import Symbol
from unittest.mock import patch
from pyramid_oereb.contrib.data_sources.standard.hook_methods import get_symbol


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
    def mock_get_symbol(identifier, theme_config):
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
        'theme_code': 'ch.BelasteteStandorte'
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
        'theme_code': 'ch.BelasteteStandorte'
    })
    webservice = mock_symbol_fail(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()


@pytest.fixture(autouse=True)
def mock_get_theme_config_by_code():

    def get_theme_config_by_code(code):
        return {
            'hooks': {
                'get_symbol': 'pyramid_oereb.contrib.data_sources.standard.hook_methods.get_symbol'
            }
        }
    yield get_theme_config_by_code


def test_get_method(mock_get_theme_config_by_code):
    with patch('pyramid_oereb.core.config.Config.get_theme_config_by_code', mock_get_theme_config_by_code):
        assert Symbol.get_method('abc.xyz') == get_symbol
