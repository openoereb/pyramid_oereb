import io
import pytest
from PIL import Image
from sqlalchemy import INTEGER

from pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme import model_factory
from pyramid_oereb.contrib.data_sources.interlis_2_3.interlis_2_3_utils \
    import from_multilingual_uri_to_dict, from_multilingual_blob_to_dict, from_multilingual_text_to_dict


@pytest.fixture(scope="session")
def png_binary_1():
    output = io.BytesIO()
    Image.new("RGB", (72, 36), (0, 0, 0)).save(output, format='PNG')
    yield output.getvalue()


@pytest.fixture(scope="session")
def png_binary_2():
    output = io.BytesIO()
    Image.new("RGB", (72, 36), (128, 128, 128)).save(output, format='PNG')
    yield output.getvalue()


@pytest.fixture(scope="session")
def png_binary_3():
    output = io.BytesIO()
    Image.new("RGB", (72, 36), (255, 255, 255)).save(output, format='PNG')
    yield output.getvalue()


@pytest.fixture(scope="session")
def model_example1():
    models = model_factory("interlis_utils_test", INTEGER, 2056, "")
    model = models
    local_uri = models.LocalisedUri()
    local_uri.language = "de"
    local_uri.text = "Beispiel 1"
    local_uri2 = models.LocalisedUri()
    local_uri2.language = "fr"
    local_uri2.text = "Exemple 1"
    model.localised_uri = [local_uri, local_uri2]
    yield [model]


@pytest.fixture(scope="session")
def model_example2():
    models = model_factory("interlis_utils_test", INTEGER, 2056, "")
    model = models
    local_uri = models.LocalisedUri()
    local_uri.language = "it"
    local_uri.text = "Esempio 2"
    model.localised_uri = [local_uri]
    yield [model]


@pytest.fixture(scope="session")
def model_example_blob(png_binary_1, png_binary_2):
    models = model_factory("interlis_utils_test", INTEGER, 2056, "")
    model = models
    local_uri = models.LocalisedUri()
    local_uri.language = "de"
    local_uri.blob = png_binary_1
    local_uri2 = models.LocalisedUri()
    local_uri2.language = "fr"
    local_uri2.blob = png_binary_2
    model.localised_blob = [local_uri, local_uri2]
    yield [model]


@pytest.fixture(scope="session")
def model_example_blob2(png_binary_3):
    models = model_factory("interlis_utils_test", INTEGER, 2056, "")
    model = models
    local_uri = models.LocalisedUri()
    local_uri.language = "it"
    local_uri.blob = png_binary_3
    model.localised_blob = [local_uri]
    yield [model]


def test_from_multilingual_uri_to_dict(model_example1, model_example2):
    dict_1 = from_multilingual_uri_to_dict(model_example1)
    dict_2 = from_multilingual_uri_to_dict(model_example2)

    dict_1_keys = list(dict_1.keys())
    dict_1_keys.sort()
    dict_1 = {i: dict_1[i] for i in dict_1_keys}

    dict_2_keys = list(dict_2.keys())
    dict_2_keys.sort()
    dict_2 = {i: dict_2[i] for i in dict_2_keys}

    assert dict_1 == {"de": "Beispiel 1", "fr": "Exemple 1"}
    assert dict_2 == {"it": "Esempio 2"}


def test_from_multilingual_blob_to_dict(png_binary_1, png_binary_2, png_binary_3,
                                        model_example_blob, model_example_blob2):
    dict_1 = from_multilingual_blob_to_dict(model_example_blob)
    dict_2 = from_multilingual_blob_to_dict(model_example_blob2)

    dict_1_keys = list(dict_1.keys())
    dict_1_keys.sort()
    dict_1 = {i: dict_1[i] for i in dict_1_keys}

    dict_2_keys = list(dict_2.keys())
    dict_2_keys.sort()
    dict_2 = {i: dict_2[i] for i in dict_2_keys}

    assert dict_1 == {"de": png_binary_1, "fr": png_binary_2}
    assert dict_2 == {"it": png_binary_3}


def test_from_multilingual_text_to_dict():
    result_dict = from_multilingual_text_to_dict(de="Beispiel", fr="Exemple", it="Esempio",
                                                 rm="Exempel", en="Example")
    assert result_dict == {
        "de": "Beispiel",
        "fr": "Exemple",
        "it": "Esempio",
        "rm": "Exempel",
        "en": "Example"
    }


def test_from_multilingual_text_to_dict_some_None():
    result_dict = from_multilingual_text_to_dict(de="Beispiel", it="Esempio", en="Example")
    assert result_dict == {
        "de": "Beispiel",
        "it": "Esempio",
        "en": "Example"
    }


def test_from_multilingual_text_to_dict_all_None():
    result_dict = from_multilingual_text_to_dict(de=None, fr=None, it=None, rm=None, en=None)
    assert result_dict is None
