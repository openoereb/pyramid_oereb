# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.reference_definition import ReferenceDefinitionRecord
from pyramid_oereb.lib.records.office import OfficeRecord


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
