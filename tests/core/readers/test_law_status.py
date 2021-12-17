# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.law_status import LawStatusReader


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
        LawStatus(**{
            "code": "AenderungMitVorwirkung",
            "title": {
                "de": "Änderung mit Vorwirkung",
                "fr": "Modification avec effet anticipé",
                "it": "Modifica con effetto anticipato",
                "rm": "Midada cun effect anticipà",
                "en": "Modification with pre-effect"
            }
        }),
        LawStatus(**{
            "code": "AenderungOhneVorwirkung",
            "title": {
                "de": "Änderung ohne Vorwirkung",
                "fr": "Modification sans effet anticipé",
                "it": "Modifica senza effetto anticipato",
                "rm": "Midada senza effect anticipà",
                "en": "Modification without pre-effect"
            }
        }),
    ]
    dbsession.add_all(law_statuses)
    dbsession.flush()
    yield law_statuses


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    reader = LawStatusReader(
        pyramid_oereb_test_config.get_law_status_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_law_status_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config, law_status_data):

    reader = LawStatusReader(
        pyramid_oereb_test_config.get_law_status_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_law_status_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 3
    result = results[0]
    assert isinstance(result, LawStatusRecord)
    assert result.code == law_status_data[0].code
    assert result.title['fr'] == law_status_data[0].title['fr']
