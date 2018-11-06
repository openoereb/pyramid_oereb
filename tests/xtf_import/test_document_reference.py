# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.document_reference import DocumentReference


def test_init():
    document_reference = DocumentReference('foo', 'bar')
    assert document_reference._session == 'foo'
    assert document_reference._model == 'bar'
