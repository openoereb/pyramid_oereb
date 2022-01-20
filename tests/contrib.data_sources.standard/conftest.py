import pytest
from unittest.mock import patch


@pytest.fixture
def session():

    class Session:
        def query(self, model):
            return
        def close(self):
            return

    yield Session

@pytest.fixture
def query():

    class Query:
        def filter(self, term):
            return self
        def one(self):
            return

    yield Query


@pytest.fixture(autouse=True)
def srid():
    def srid():
        return 2056
    with patch('pyramid_oereb.core.config.Config.get_srid', srid):
        yield