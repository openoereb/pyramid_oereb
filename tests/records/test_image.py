# -*- coding: utf-8 -*-

import sys
import base64


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
