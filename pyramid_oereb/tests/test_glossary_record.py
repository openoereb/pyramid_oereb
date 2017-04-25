# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.glossary import GlossaryRecord


def test_get_fields():
    expected_fields = [
        'id',
        'title',
        'content'
    ]
    fields = GlossaryRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        GlossaryRecord()


def test_init():
    record = GlossaryRecord(id=1, title=u'SGRF', content=u'Service de la géomatique et du registre foncier')
    assert record.title == u'SGRF'
    assert record.content is not None
    assert isinstance(record.content, unicode)


def test_to_extract():
    assert GlossaryRecord(
        1, 
        u'SGRF', 
        u'Service de la géomatique et du registre foncier'
    ).to_extract() == {
        'id': 1,
        'title': u'SGRF',
        'content': u'Service de la géomatique et du registre foncier'
    }
