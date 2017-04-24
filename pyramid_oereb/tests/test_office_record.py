# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.office import OfficeRecord


def test_get_fields():
    expected_fields = [
            'name',
            'uid',
            'office_at_web',
            'line1',
            'line2',
            'street',
            'number',
            'postal_code',
            'city'
    ]
    fields = OfficeRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        OfficeRecord()


def test_init():
    record = OfficeRecord(name='a', uid='ch99', postal_code=4123)
    assert record.name == 'a'
    assert record.line1 is None
    assert isinstance(record.postal_code, int)


def test_to_extract():
    assert OfficeRecord('home office', office_at_web='http://ho.work.org').to_extract() == {
        'name': 'home office',
        'office_at_web': 'http://ho.work.org'
    }
    assert OfficeRecord(
        'test office',
        uid='test-uid',
        office_at_web='http://office.test.org',
        line1='address line 1',
        line2='address line 2',
        street='office street',
        number='1a',
        postal_code='1234',
        city='workaholic city'
    ).to_extract() == {
        'name': 'test office',
        'uid': 'test-uid',
        'office_at_web': 'http://office.test.org',
        'line1': 'address line 1',
        'line2': 'address line 2',
        'street': 'office street',
        'number': '1a',
        'postal_code': '1234',
        'city': 'workaholic city'
    }
