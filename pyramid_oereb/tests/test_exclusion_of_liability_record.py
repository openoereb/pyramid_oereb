# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.office import ExclusionOfLiabilityRecord


def test_get_fields():
    expected_fields = [
            'title',
            'content'
    ]
    fields = ExclusionOfLiabilityRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ExclusionOfLiabilityRecord()


def test_init():
    record = ExclusionOfLiabilityRecord(title='Disclaimer', content=u'No warranty on nothing.')
    assert record.title == 'Discclaimer'
    assert record.content is not None
    assert isinstance(record.content, UnicodeType)
