# -*- coding: utf-8 -*-
import base64


from pyramid_oereb.lib.records.image import ImageRecord


def test_init():
    image_record = ImageRecord(bin(1))
    assert isinstance(image_record.content, str)


def test_encode():
    image_record = ImageRecord(bin(1))
    assert image_record.encode() == base64.b64encode(bin(1))
