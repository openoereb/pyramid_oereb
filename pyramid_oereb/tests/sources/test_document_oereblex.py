# -*- coding: utf-8 -*-
import datetime
import pytest
from geolink_formatter.entity import Document, File

from pyramid_oereb.lib.sources.document import OEREBlexSource


@pytest.mark.parametrize('valid,cfg', [
    (True, {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'canton': 'BL'
    }),
    (False, {
        'language': 'de',
        'canton': 'BL'
    }),
    (False, {
        'host': 'http://oereblex.example.com',
        'language': 'german',
        'canton': 'BL'
    }),
    (False, {
        'host': 'http://oereblex.example.com',
        'language': 'de'
    })
])
def test_init(valid, cfg):
    if valid:
        assert isinstance(OEREBlexSource(**cfg), OEREBlexSource)
    else:
        with pytest.raises(AssertionError):
            OEREBlexSource(**cfg)


@pytest.mark.parametrize('key,multilingual,result', [
    ('official_title', False, None),
    ('municipality', False, 'Liestal'),
    ('municipality', True, {'de': 'Liestal'})
])
def test_get_mapped_value(key, multilingual, result):
    file_ = File('Test', '/api/attachments/1', 'main')
    document = Document('test', 'Test', 'main', 'decree', [file_], datetime.date.today(), subtype='Liestal')
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                            mapping={'municipality': 'subtype'})
    assert source._get_mapped_value(document, key, multilingual) == result
