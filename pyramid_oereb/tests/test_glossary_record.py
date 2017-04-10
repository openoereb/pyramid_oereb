# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.glossary import GlossaryRecord


def test_get_fields():
    expected_fields = [
            'title',
            'content'
    ]
    fields = GlossaryRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        GlossaryRecord()


def test_init():
    record = GlossaryRecord(title='SGRF', content=u'Service de la géomatique et du registre foncier')
    assert record.title == 'SGRF'
    assert record.content is not None
    assert isinstance(record.content, unicode)
