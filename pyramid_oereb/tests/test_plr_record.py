# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.plr import PlrRecord


def test_get_fields():
    expected_fields = [
        'topic',
        'documents',
        'geometries',
        'view_service',
        'refinements',
        'additional_topic',
        'content',
        'type_code_list',
        'type_code',
        'basis',
        'published_from',
        'legal_state',
        'subtopic'
    ]
    fields = PlrRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        PlrRecord()


def test_init():
    record = PlrRecord(content='a', topic='b', legal_state='c', published_from='d')
    assert record.content == 'a'
    assert record.subtopic is None
    assert isinstance(record.geometries, list)
