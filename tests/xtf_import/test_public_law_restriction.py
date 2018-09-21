# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.public_law_restriction import PublicLawRestriction


def test_init():
    public_law_restriction = PublicLawRestriction('foo', 'bar', 'baz')
    assert public_law_restriction._session == 'foo'
    assert public_law_restriction._model == 'bar'
    assert public_law_restriction._topic_code == 'baz'
