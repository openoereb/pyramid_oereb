# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.views.webservice import Parameter, QRcode


@pytest.fixture
def extract_url():
    yield 'http://localhost:6543/oereb/extract/xml?EGRID=CH113928077734'


@pytest.fixture
def qr_code_ref(extract_url):
    yield 'http://localhost:6543/oereb/image' \
          '/qrcode?extract_url={}'.format(extract_url)


def test_parameter(extract_url, qr_code_ref):
    params = Parameter(
        'json',
        True,
        False,
        True,
        extract_url=extract_url,
        qr_code_ref=qr_code_ref
    )
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
    assert params.qr_code_ref == qr_code_ref
    assert params.extract_url == extract_url
    assert params.qr_code == QRcode.create_qr_code(extract_url)
