# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.adapter import DatabaseAdapter
from pyramid_oereb.contrib.data_sources.standard.sources.disclaimer import DatabaseSource
from pyramid_oereb.contrib.data_sources.standard.models import Disclaimer
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init():
    source = DatabaseSource(
        **Config.get_disclaimer_config().get('source').get('params')
    )
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Disclaimer


@pytest.mark.run(order=2)
def test_read():
    source = DatabaseSource(
        **Config.get_disclaimer_config().get('source').get('params')
    )
    source.read(MockParameter())
    assert len(source.records) == 1
