# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.document_types import DocumentTypeRecord


def test_document_type_init():
    record = DocumentTypeRecord(u'code', {u'de': u'Gesetzliche Grundlage'})
    assert record.code == u'code'
    assert record.title == {
        u'de': u'Gesetzliche Grundlage'
    }


@pytest.mark.filterwarnings("ignore:Type of")
def test_wrong_types():
    record = DocumentTypeRecord({'de': 'titel'}, 'content')
    assert isinstance(record.code, dict)
    assert isinstance(record.title, str)
