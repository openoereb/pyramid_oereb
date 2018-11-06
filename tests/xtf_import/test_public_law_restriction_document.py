# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.public_law_restriction_document import PublicLawRestrictionDocument


def test_init():
    public_law_restriction_document = PublicLawRestrictionDocument('foo', 'bar')
    assert public_law_restriction_document._session == 'foo'
    assert public_law_restriction_document._model == 'bar'
