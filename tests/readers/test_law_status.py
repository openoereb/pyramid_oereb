# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.law_status import LawStatusReader


@pytest.mark.run(order=2)
def test_init():
    reader = LawStatusReader(
        Config.get_law_status_config().get('source').get('class'),
        **Config.get_law_status_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read():
    reader = LawStatusReader(
        Config.get_law_status_config().get('source').get('class'),
        **Config.get_law_status_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 3
    result = results[0]
    assert isinstance(result, LawStatusRecord)
    assert result.code == 'inKraft'
    assert result.text['fr'] == 'En vigueur'
