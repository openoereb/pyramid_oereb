# -*- coding: utf-8 -*-
from pyramid_oereb.contrib.data_sources.standard.xtf_import import BaseRefinement


def test_init():
    base_refinement = BaseRefinement('foo', 'bar', 'baz')
    assert base_refinement._session == 'foo'
    assert base_refinement._model_base == 'bar'
    assert base_refinement._model_refinement == 'baz'
