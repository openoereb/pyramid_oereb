# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.law_status import LawStatusReader


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    reader = LawStatusReader(
        pyramid_oereb_test_config.get_law_status_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_law_status_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config):
    reader = LawStatusReader(
        pyramid_oereb_test_config.get_law_status_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_law_status_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 3
    result = results[0]
    assert isinstance(result, LawStatusRecord)
    assert result.code == 'inKraft'
    assert result.title['fr'] == 'En vigueur'
