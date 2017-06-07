# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.office import OfficeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        OfficeRecord()


def test_init():
    record = OfficeRecord(name='a', uid='ch99', postal_code=4123)
    assert record.name == 'a'
    assert record.line1 is None
    assert isinstance(record.postal_code, int)
