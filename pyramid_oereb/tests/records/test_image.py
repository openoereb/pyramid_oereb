# -*- coding: utf-8 -*-
import base64
import os

from pyramid.testing import testConfig

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.tests.conftest import MockRequest


def test_init():
    image_record = ImageRecord('image content', '/image/source')
    assert isinstance(image_record.content, str)
    assert isinstance(image_record.source, str)


def test_encode():
    image_record = ImageRecord('image content', '/image/source')
    assert image_record.encode() == base64.b64encode('image content')


def test_from_file():
    image_record = ImageRecord.from_file('pyramid_oereb/standard/images/logos/logo_oereb.png')
    assert isinstance(image_record, ImageRecord)


def test_get_url():
    with testConfig() as config:
        config.add_static_view('images', os.path.abspath('pyramid_oereb/standard/images'))
        image_record = ImageRecord.from_file('pyramid_oereb/standard/images/logos/logo_oereb.png')
        assert isinstance(image_record, ImageRecord)
        request = MockRequest()
        url = image_record.get_url(request)
        assert url == 'http://example.com/images/logos/logo_oereb.png'
