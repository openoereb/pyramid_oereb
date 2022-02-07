import pytest

from unittest.mock import patch


@pytest.fixture()
def app_config():
    yield {
        "srid": 2056,
        "app_schema": {
            "name": "test",
            "models": "pyramid_oereb.contrib.data_sources.standard.models.main",
            "db_connection": "postgresql://postgres:postgres@123.123.123.123:5432/pyramid_oereb_test"
        }
    }


@pytest.fixture(autouse=True)
def config(app_config):
    with patch('pyramid_oereb.core.config.Config._config', app_config):
        yield


@pytest.fixture(autouse=True)
def health_check():
    def mock_check(inst):
        return True
    with patch('pyramid_oereb.core.sources.BaseDatabaseSource.health_check', mock_check):
        yield
