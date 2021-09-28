# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.disclaimer import DisclaimerReader
from pyramid_oereb.lib.records.disclaimer import DisclaimerRecord
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init():
    reader = DisclaimerReader(
        Config.get_disclaimer_config().get('source').get('class'),
        **Config.get_disclaimer_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read():
    reader = DisclaimerReader(
        Config.get_disclaimer_config().get('source').get('class'),
        **Config.get_disclaimer_config().get('source').get('params')
    )
    results = reader.read(MockParameter())
    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], DisclaimerRecord)
    assert len(results[0].title) == 4
    assert len(results[0].content) == 4
    assert 'du cadastre des sites' in results[0].title['fr']
    assert 'Kataster der belasteten Standorte' in results[0].content['de']
