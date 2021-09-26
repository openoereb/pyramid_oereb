# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.standard.sources.disclaimer import DatabaseSource
from pyramid_oereb.standard.models.main import Disclaimer
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
