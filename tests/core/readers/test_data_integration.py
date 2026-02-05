# -*- coding: utf-8 -*-
from pyramid_oereb.core.readers.data_integration import DataIntegrationReader
from pyramid_oereb.core.sources.data_integration import DataIntegrationBaseSource


class MockSource(DataIntegrationBaseSource):
    def __init__(self, **params):
        super(MockSource, self).__init__(**params)

    def read(self):
        return ['fake_record']


def test_read():
    dotted_path = 'tests.core.readers.test_data_integration.MockSource'
    reader = DataIntegrationReader(dotted_path)
    results = reader.read()
    assert results == ['fake_record']
