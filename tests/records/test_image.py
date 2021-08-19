# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib import b64
from pyramid_oereb.lib.adapter import FileAdapter
from pyramid_oereb.lib.records.image import ImageRecord


def test_init():
    image_record = ImageRecord('1'.encode('utf-8'))
    assert isinstance(image_record.content, bytes)


def test_encode():
    image_record = ImageRecord('1'.encode('utf-8'))
    assert image_record.encode() == b64.encode('1'.encode('utf-8'))


def test_validate_filetype_png_file():
    assert ImageRecord._validate_filetype('tests/resources/logo_canton.png') == ('png', 'image/png')


def test_validate_filetype_png_content():
    content = FileAdapter().read('tests/resources/logo_canton.png')
    assert ImageRecord._validate_filetype(content) == ('png', 'image/png')


def test_validate_filetype_svg_file():
    assert ImageRecord._validate_filetype('tests/resources/python.svg') == ('svg', 'image/svg+xml')


def test_validate_filetype_svg_content():
    content = FileAdapter().read('tests/resources/python.svg')
    assert ImageRecord._validate_filetype(content) == ('svg', 'image/svg+xml')


def test_validate_filetype_unrecognized():
    with pytest.raises(TypeError) as e:
        ImageRecord._validate_filetype('tests/resources/test_config.yml')
    assert '{0}'.format(e.value) == 'Unrecognized file type'


def test_validate_filetype_invalid():
    with pytest.raises(TypeError) as e:
        ImageRecord._validate_filetype('tests/resources/invalid.jpg')
    assert '{0}'.format(e.value).startswith('Invalid file type')
