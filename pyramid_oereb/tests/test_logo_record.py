# -*- coding: utf-8 -*-
import base64
from pyramid_oereb.lib.records.logo import LogoRecord


def test_get_fields():
    expected_fields = [
        'content'
    ]
    fields = LogoRecord.get_fields()
    assert fields == expected_fields


def test_init():
    logo_record = LogoRecord('string to test')
    assert isinstance(logo_record.content, str)


def test_to_extract():
    logo_record = LogoRecord('string to test')
    assert logo_record.to_extract() == {
        'content': base64.b64encode('string to test')
    }
