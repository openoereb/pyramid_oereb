import pytest
import io

from unittest.mock import patch
from PIL import Image

from pyramid_oereb.core.records.law_status import LawStatusRecord


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


@pytest.fixture
def law_status_records():
    yield [
        LawStatusRecord(
            "inKraft",
            {
                "de": "Rechtskräftig",
                "fr": "En vigueur",
                "it": "In vigore",
                "rm": "En vigur",
                "en": "In force"
            }
        ),
        LawStatusRecord(
            "AenderungMitVorwirkung",
            {
                "de": "Änderung mit Vorwirkung",
                "fr": "Modification avec effet anticipé",
                "it": "Modifica con effetto anticipato",
                "rm": "Midada cun effect anticipà",
                "en": "Modification with pre-effect"
            }
        ),
        LawStatusRecord(
            "AenderungOhneVorwirkung",
            {
                "de": "Änderung ohne Vorwirkung",
                "fr": "Modification sans effet anticipé",
                "it": "Modifica senza effetto anticipato",
                "rm": "Midada senza effect anticipà",
                "en": "Modification without pre-effect"
            }
        )
    ]
