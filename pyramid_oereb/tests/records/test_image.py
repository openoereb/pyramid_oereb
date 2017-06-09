# -*- coding: utf-8 -*-
import base64
from pyramid_oereb.lib.records.image import ImageRecord


def test_init():
    logo_record = ImageRecord('string to test')
    assert isinstance(logo_record.content, str)


def test_encode():
    logo_record = ImageRecord('image content')
    assert logo_record.encode() == base64.b64encode('image content')
