import pytest
import io

from unittest.mock import patch
from PIL import Image


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


@pytest.fixture
def png_image():
    yield Image.new("RGB", (72, 36), (128, 128, 128))


@pytest.fixture
def png_binary(png_image):
    output = io.BytesIO()
    png_image.save(output, format='PNG')
    yield output.getvalue()
