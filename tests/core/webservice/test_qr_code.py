# -*- coding: utf-8 -*-

import pytest
import io
import qrcode
from pyramid.httpexceptions import HTTPNoContent
from pyramid.response import Response
from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import QRcode


@pytest.fixture
def png_image():
    qr = qrcode.QRCode()
    qr.add_data('http://qr-example.abc')
    qr.make()
    yield qr.make_image()


@pytest.fixture
def png_binary(png_image):
    output = io.BytesIO()
    png_image.save(output, format='PNG')
    yield output.getvalue()


def get_qr_code(png_binary):
    request = MockRequest()
    request.params.update({
        'extract_url': 'http://qr-example.abc'
    })
    webservice = QRcode(request)
    result = webservice.get_qr_code()
    assert isinstance(result, Response)
    assert result.body == png_binary
    assert result.status_int == 200
    assert result.content_type == 'image/png'


def test_missing_parameter():
    request = MockRequest()
    webservice = QRcode(request)
    with pytest.raises(HTTPNoContent):
        webservice.get_qr_code()


def test_create_qr_code(png_binary):
    assert QRcode.create_qr_code('http://qr-example.abc') == png_binary


def test_sanitize_url():
    assert QRcode.sanitize_url('http://qr-example.abc') == 'http://qr-example.abc'
