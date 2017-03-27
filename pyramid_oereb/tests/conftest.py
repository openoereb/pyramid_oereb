# -*- coding: utf-8 -*-
import pytest
import pyramid.testing
import transaction

from pyramid_oereb import routes
from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.config import parse

db_url = parse('pyramid_oereb_test.yml', 'pyramid_oereb').get('db_connection')
adapter = DatabaseAdapter()


@pytest.yield_fixture
def config():
    config = pyramid.testing.setUp()
    tx = transaction.begin()
    tx.doom()
    yield config
    tx.abort()
    pyramid.testing.tearDown()


@pytest.fixture
def example_api(config):
    return routes.create_test_api(config)
