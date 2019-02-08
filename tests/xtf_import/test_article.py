# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.article import Article


def test_init():
    article = Article('foo', 'bar')
    assert article._session == 'foo'
    assert article._model == 'bar'
