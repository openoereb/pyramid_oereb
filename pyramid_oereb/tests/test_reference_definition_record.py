# -*- coding: utf-8 -*-

__author__ = 'François Voisard'
__create_date__ = '28.03.2017'

import pytest

from pyramid_oereb.lib.records.reference_definition import ReferenceDefinitionRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_get_fields():
    expected_fields = [
            'topic',
            'canton',
            'municipality',
            'responsible_office'
    ]
    fields = ReferenceDefinitionRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ReferenceDefinitionRecord()


def test_init():
    office_record = OfficeRecord('name')
    record = ReferenceDefinitionRecord(topic='a', canton=None, municipality='Liestal',
                                       responsible_office=office_record)
    assert record.topic == 'a'
    assert record.canton is None
    assert isinstance(record.municipality, str)
    assert isinstance(record.responsible_office, OfficeRecord)
