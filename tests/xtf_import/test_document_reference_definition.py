# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.document_reference_definition import DocumentReferenceDefinition


def test_init():
    document_reference_definition = DocumentReferenceDefinition('foo', 'bar')
    assert document_reference_definition._session == 'foo'
    assert document_reference_definition._model == 'bar'
