# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.glossary import GlossaryDatabaseSource
from pyramid_oereb.standard.models.main import Glossary


@pytest.mark.run(order=2)
def test_init(config_reader):
    source = GlossaryDatabaseSource(**config_reader.get_glossary_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Glossary


@pytest.mark.run(order=2)
def test_read(config_reader):
    source = GlossaryDatabaseSource(**config_reader.get_glossary_config().get('source').get('params'))
    source.read()
