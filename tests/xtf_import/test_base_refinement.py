# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.base_refinement import BaseRefinement


def test_init():
    base_refinement = BaseRefinement('foo', 'bar', 'baz')
    assert base_refinement._session == 'foo'
    assert base_refinement._model_base == 'bar'
    assert base_refinement._model_refinement == 'baz'
