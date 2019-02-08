# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.reference_definition import ReferenceDefinition


def test_init():
    reference_definition = ReferenceDefinition('foo', 'bar', 'baz')
    assert reference_definition._session == 'foo'
    assert reference_definition._model == 'bar'
    assert reference_definition._topic_code == 'baz'
