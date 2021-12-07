# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.disclaimer import DisclaimerReader
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    reader = DisclaimerReader(
        pyramid_oereb_test_config.get_disclaimer_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_disclaimer_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config):
    reader = DisclaimerReader(
        pyramid_oereb_test_config.get_disclaimer_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_disclaimer_config().get('source').get('params')
    )
    results = reader.read(MockParameter())
    assert isinstance(results, list)
    assert len(results) == 2
    assert isinstance(results[0], DisclaimerRecord)
    assert len(results[0].title) == 5
    assert len(results[0].content) == 5
    assert 'dans le registre foncier' in results[0].title['fr']
    assert 'Eigentumsbeschränkungen' in results[0].content['de']
