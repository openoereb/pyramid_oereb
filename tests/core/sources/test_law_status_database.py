# -*- coding: utf-8 -*-

import pytest

from tests.mockrequest import MockParameter

from pyramid_oereb.core.adapter import DatabaseAdapter


@pytest.fixture
def law_status_data(dbsession, transact):
    from pyramid_oereb.contrib.data_sources.standard.models.main import LawStatus
    del transact
    law_statuses = [
        LawStatus(**{
            "code": "inKraft",
            "title": {
                "de": "Rechtskräftig",
                "fr": "En vigueur",
                "it": "In vigore",
                "rm": "En vigur",
                "en": "In force"
            }
        }),
    ]
    dbsession.add_all(law_statuses)
    dbsession.flush()
    yield law_statuses


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.sources.law_status import DatabaseSource
    from pyramid_oereb.contrib.data_sources.standard.models.main import LawStatus

    source = DatabaseSource(**pyramid_oereb_test_config.get_law_status_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == LawStatus


def test_read(pyramid_oereb_test_config, law_status_data):
    from pyramid_oereb.contrib.data_sources.standard.sources.law_status import DatabaseSource

    source = DatabaseSource(**pyramid_oereb_test_config.get_law_status_config().get('source').get('params'))
    source.read(MockParameter())
    assert isinstance(source.records, list)
    assert source.records[0].code == law_status_data[0].code
