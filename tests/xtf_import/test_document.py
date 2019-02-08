# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.document import Document


def test_init():
    document = Document('foo', 'bar')
    assert document._session == 'foo'
    assert document._model == 'bar'
