# -*- coding: utf-8 -*-

import pytest

from tests.mockrequest import MockParameter

from pyramid_oereb.core.adapter import DatabaseAdapter



@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.sources.disclaimer import DatabaseSource
    from pyramid_oereb.contrib.data_sources.standard.models.main import Disclaimer
    source = DatabaseSource(
        **pyramid_oereb_test_config.get_disclaimer_config().get('source').get('params')
    )
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Disclaimer


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.sources.disclaimer import DatabaseSource

    source = DatabaseSource(
        **pyramid_oereb_test_config.get_disclaimer_config().get('source').get('params')
    )
    source.read(MockParameter())
    assert len(source.records) == 1
