import pytest
import os
import pyramid.testing
import transaction
from pyramid.config import ConfigurationError

from pyramid_oereb import routes

DB_URL = os.environ.get('SQLALCHEMY_URL')


@pytest.yield_fixture
def config():
    from pyramid_oereb.standard import create_tables
    config = pyramid.testing.setUp()
    config.include('pyramid_georest')
    if DB_URL:
        create_tables(DB_URL)
    else:
        raise ConfigurationError()
    tx = transaction.begin()
    tx.doom()
    yield config
    tx.abort()
    pyramid.testing.tearDown()


@pytest.fixture
def example_api(config):
    return routes.create_test_api(config)
