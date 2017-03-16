import pytest
import os
import pyramid.testing
import transaction

from pyramid_oereb import routes
from pyramid_oereb.lib.adapter import DatabaseAdapter

DB_URL = os.environ.get('SQLALCHEMY_URL')
adapter = DatabaseAdapter()


@pytest.yield_fixture
def config():
    config = pyramid.testing.setUp()
    config.include('pyramid_georest')
    tx = transaction.begin()
    tx.doom()
    yield config
    tx.abort()
    pyramid.testing.tearDown()


@pytest.fixture
def example_api(config):
    return routes.create_test_api(config)
