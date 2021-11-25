# -*- coding: utf-8 -*-
from pyramid_oereb.contrib.data_sources.standard.xtf_import import Office


def test_init():
    office = Office('foo', 'bar')
    assert office._session == 'foo'
    assert office._model == 'bar'
