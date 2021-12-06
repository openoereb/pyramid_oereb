# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.office import OfficeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        OfficeRecord()


def test_init():
    record = OfficeRecord(
        {'de': 'Test'},
        office_at_web={'de': 'www.example.com'},
        uid='ch99',
        postal_code=4123
        )
    assert record.name.get('de') == 'Test'
    assert record.office_at_web.get('de') == 'www.example.com'
    assert record.line1 is None
    assert isinstance(record.postal_code, int)
