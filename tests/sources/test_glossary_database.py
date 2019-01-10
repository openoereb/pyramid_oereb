# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.standard.sources.glossary import DatabaseSource
from pyramid_oereb.standard.models.main import Glossary


@pytest.mark.run(order=2)
def test_init():
    source = DatabaseSource(**Config.get_glossary_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Glossary


@pytest.mark.run(order=2)
def test_read():
    source = DatabaseSource(**Config.get_glossary_config().get('source').get('params'))
    source.read()
