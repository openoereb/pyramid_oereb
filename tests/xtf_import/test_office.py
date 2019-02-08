# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.office import Office


def test_init():
    office = Office('foo', 'bar')
    assert office._session == 'foo'
    assert office._model == 'bar'
