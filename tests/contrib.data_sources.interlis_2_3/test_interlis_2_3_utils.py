import io
import pytest
from PIL import Image
from sqlalchemy import INTEGER, text, orm, create_engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy.engine.url import URL

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
def interlis_utils_db_engine(base_engine):
    # def test_db_engine(base_engine, test_db_name, config_path):
    # """
    # create a new test DB called test_db_name and its engine
    # """

    test_interlis_db_name = "interlis_utils_test"
    with base_engine.begin() as base_connection:
        # terminate existing connections to be able to DROP the DB
        term_stmt = 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity ' \
            f'WHERE pg_stat_activity.datname = \'{test_interlis_db_name}\' AND pid <> pg_backend_pid();'
        base_connection.execute(text(term_stmt))
        # sqlalchemy uses transactions by default, COMMIT end the current transaction and allows
        # creation and destruction of DB
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"DROP DATABASE if EXISTS {test_interlis_db_name}"))
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"CREATE DATABASE {test_interlis_db_name}"))

    test_db_url = URL.create(
        base_engine.url.get_backend_name(),
        base_engine.url.username,
        base_engine.url.password,
        base_engine.url.host,
        base_engine.url.port,
        database=test_interlis_db_name
    )
    engine = create_engine(test_db_url)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION POSTGIS"))
        connection.execute(CreateSchema('interlis_utils_test', if_not_exists=True))
    return engine


@pytest.fixture(scope="session")
def test_data_session(interlis_utils_db_engine, png_binary_1, png_binary_2, png_binary_3):
    session = orm.sessionmaker(bind=interlis_utils_db_engine)()
    models = model_factory("interlis_utils_test", INTEGER, 2056, interlis_utils_db_engine.url)
    models.Base.metadata.create_all(interlis_utils_db_engine)

    # Multilingual URI
    session.add(
        models.MultilingualUri(
            t_id=1
        )
    )
    session.add(
        models.MultilingualUri(
            t_id=2
        )
    )

    # Localised URI
    session.add(
        models.LocalisedUri(
            t_id=3,
            language="fr",
            text="Exemple 1",
            multilingualuri_id=1
        )
    )
    session.add(
        models.LocalisedUri(
            t_id=4,
            language="de",
            text="Beispiel 1",
            multilingualuri_id=1,
        )
    )
    session.add(
        models.LocalisedUri(
            t_id=5,
            language="it",
            text="Esempio 2",
            multilingualuri_id=2
        )
    )

    # Multilingual BLOB
    session.add(
        models.MultilingualBlob(
            t_id=6
        )
    )
    session.add(
        models.MultilingualBlob(
            t_id=7
        )
    )

    # Localised BLOB
    session.add(
        models.LocalisedBlob(
            t_id=8,
            language="de",
            blob=png_binary_1,
            multilingualblob_id=6
        )
    )
    session.add(
        models.LocalisedBlob(
            t_id=9,
            language="fr",
            blob=png_binary_2,
            multilingualblob_id=6
        )
    )
    session.add(
        models.LocalisedBlob(
            t_id=10,
            language="it",
            blob=png_binary_3,
            multilingualblob_id=7
        )
    )

    session.commit()
    yield session


def test_from_multilingual_uri_to_dict(interlis_utils_db_engine, test_data_session):
    models = model_factory("interlis_utils_test", INTEGER, 2056, interlis_utils_db_engine.url)
    session = test_data_session
    result_1 = session.query(models.MultilingualUri).filter(models.MultilingualUri.t_id == 1)
    result_2 = session.query(models.MultilingualUri).filter(models.MultilingualUri.t_id == 2)

    dict_1 = from_multilingual_uri_to_dict(result_1)
    dict_2 = from_multilingual_uri_to_dict(result_2)

    dict_1_keys = list(dict_1.keys())
    dict_1_keys.sort()
    dict_1 = {i: dict_1[i] for i in dict_1_keys}

    dict_2_keys = list(dict_2.keys())
    dict_2_keys.sort()
    dict_2 = {i: dict_2[i] for i in dict_2_keys}

    assert dict_1 == {"de": "Beispiel 1", "fr": "Exemple 1"}
    assert dict_2 == {"it": "Esempio 2"}


def test_from_multilingual_blob_to_dict(interlis_utils_db_engine, test_data_session,
                                        png_binary_1, png_binary_2, png_binary_3):
    models = model_factory("interlis_utils_test", INTEGER, 2056, interlis_utils_db_engine.url)
    session = test_data_session
    result_1 = session.query(models.MultilingualBlob).filter(models.MultilingualBlob.t_id == 6)
    result_2 = session.query(models.MultilingualBlob).filter(models.MultilingualBlob.t_id == 7)

    dict_1 = from_multilingual_blob_to_dict(result_1)
    dict_2 = from_multilingual_blob_to_dict(result_2)

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
