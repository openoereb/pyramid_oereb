# -*- coding: utf-8 -*-

from pyramid_oereb.views.webservice import Parameter


def test_parameter():
    params = Parameter('reduced', 'json', True, False)
    params.set_identdn('identdn')
    params.set_number('1000')
    params.set_egrid('EGRID')
    params.set_language('de')
    params.set_topics(['topic1', 'topic2'])
    assert params.flavour == 'reduced'
    assert params.format == 'json'
    assert params.geometry
    assert not params.images
    assert params.identdn == 'identdn'
    assert params.number == '1000'
    assert params.egrid == 'EGRID'
    assert params.language == 'de'
    assert params.topics == ['topic1', 'topic2']
