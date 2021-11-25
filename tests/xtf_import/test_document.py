# -*- coding: utf-8 -*-
from pyramid_oereb.contrib.data_sources.standard.xtf_import import Document


def test_init():
    document = Document('foo', 'bar')
    assert document._session == 'foo'
    assert document._model == 'bar'
