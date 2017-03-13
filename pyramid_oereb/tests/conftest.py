import pytest
import os
import pyramid.testing
import transaction
from pyramid.config import ConfigurationError
from sqlalchemy import create_engine

from pyramid_oereb import routes
from pyramid_oereb.models import Base

DB_URL = os.environ.get('SQLALCHEMY_URL')


@pytest.yield_fixture
def config():
    config = pyramid.testing.setUp()
    config.include('pyramid_georest')
    meta_data = Base.metadata
    if DB_URL:
        engine = create_engine(DB_URL)
    else:
        raise ConfigurationError()
    meta_data.create_all(engine)
    tx = transaction.begin()
    tx.doom()
    yield config
    tx.abort()
    pyramid.testing.tearDown()


@pytest.fixture
def example_api(config):
    return routes.create_test_api(config)
