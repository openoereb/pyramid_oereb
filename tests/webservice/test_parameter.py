# -*- coding: utf-8 -*-

from pyramid_oereb.core.views import Parameter


def test_parameter():
    params = Parameter('json', True, False, True)
    params.set_identdn('identdn')
    params.set_number('1000')
    params.set_egrid('EGRID')
    params.set_language('de')
    params.set_topics(['topic1', 'topic2'])
    assert params.format == 'json'
    assert params.with_geometry
    assert not params.images
    assert params.signed
    assert params.identdn == 'identdn'
    assert params.number == '1000'
    assert params.egrid == 'EGRID'
    assert params.language == 'de'
    assert params.topics == ['topic1', 'topic2']
