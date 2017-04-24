# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord


def test_get_fields():
    expected_fields = [
        'id',
        'title',
        'content'
    ]
    fields = ExclusionOfLiabilityRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ExclusionOfLiabilityRecord()


def test_init():
    record = ExclusionOfLiabilityRecord(id=1, title='Disclaimer', content=u'No warranty on nothing.')
    assert record.id == 1
    assert record.title == 'Disclaimer'
    assert record.content is not None
    assert isinstance(record.content, unicode)


def test_to_extract():
    assert ExclusionOfLiabilityRecord(1, 'Title', 'Content').to_extract() == {
        'id': 1,
        'title': 'Title',
        'content': 'Content'
    }
