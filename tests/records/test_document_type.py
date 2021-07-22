# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.document_types import DocumentTypeRecord


def test_document_type_init():
    record = DocumentTypeRecord(u'code', {u'de': u'Gesetzliche Grundlage'})
    assert record.code == u'code'
    assert record.text == {
        u'de': u'Gesetzliche Grundlage'
    }
