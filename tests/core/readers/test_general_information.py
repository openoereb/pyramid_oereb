# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.general_information import GeneralInformationReader
from pyramid_oereb.core.records.general_information import GeneralInformationRecord


@pytest.fixture
def general_information_data(dbsession, transact):
    from pyramid_oereb.contrib.data_sources.standard.models.main import GeneralInformation
    del transact
    general_information = [
        GeneralInformation(**{
            'id': 1,
            'title': {
                'de': u'GI1',
            },
            'content': {
                'de': u'General Information # 1',
                'fr': u'Information Generale #1',
            },
            'extract_index': 2,
        }),
        GeneralInformation(**{
            'id': 2,
            'title': {
                'de': u'GI2',
            },
            'content': {
                'de': u'General Information # 2',
                'fr': u'Information Generale #2',
            },
            'extract_index': 3,
        }),
        GeneralInformation(**{
            'id': 3,
            'title': {
                'de': u'GI3',
            },
            'content': {
                'de': u'General Information # 3',
                'fr': u'Information Generale #3',
            },
            'extract_index': 1,
        })
    ]
    dbsession.add_all(general_information)
    dbsession.flush()
    yield general_information


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    reader = GeneralInformationReader(
        pyramid_oereb_test_config.get_info_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_info_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config, general_information_data):
    reader = GeneralInformationReader(
        pyramid_oereb_test_config.get_info_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_info_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == len(general_information_data)
    assert isinstance(results[0], GeneralInformationRecord)
    assert len(results[0].title) == len(general_information_data[0].title)
    assert len(results[0].content) == len(general_information_data[0].content)
    assert 'GI3' == results[0].title['de']
    assert 'Information Generale #1' == results[1].content['fr']
    assert sorted(r.extract_index for r in results) == [r.extract_index for r in results]
