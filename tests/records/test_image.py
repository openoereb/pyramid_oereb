# -*- coding: utf-8 -*-

import sys
import base64

import pytest

from pyramid_oereb.lib.records.image import ImageRecord


def test_init():
    image_record = ImageRecord('1'.encode('utf-8'))
    if sys.version_info.major == 2:
        assert isinstance(image_record.content, str)
    else:
        assert isinstance(image_record.content, bytes)


def test_encode():
    image_record = ImageRecord('1'.encode('utf-8'))
    assert image_record.encode() == base64.b64encode('1'.encode('utf-8')).decode('ascii')


def test_validate_filetype_png_file():
    assert ImageRecord._validate_filetype('tests/resources/logo_canton.png') == ('png', 'image/png')


def test_validate_filetype_png_content():
    with open('tests/resources/logo_canton.png') as f:
        content = bytearray(f.read())
    assert ImageRecord._validate_filetype(content) == ('png', 'image/png')


def test_validate_filetype_svg_file():
    assert ImageRecord._validate_filetype('tests/resources/python.svg') == ('svg', 'image/svg+xml')


def test_validate_filetype_svg_content():
    with open('tests/resources/python.svg') as f:
        content = f.read()
    assert ImageRecord._validate_filetype(content) == ('svg', 'image/svg+xml')


def test_validate_filetype_unrecognized():
    with pytest.raises(TypeError) as e:
        ImageRecord._validate_filetype('tests/resources/test_config.yml')
    assert '{0}'.format(e.value) == 'Unrecognized file type'


def test_validate_filetype_invalid():
    with pytest.raises(TypeError) as e:
        ImageRecord._validate_filetype('tests/resources/invalid.jpg')
    assert '{0}'.format(e.value).startswith('Invalid file type')
