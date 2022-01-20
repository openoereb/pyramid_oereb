import io

import pytest
import datetime
from unittest.mock import patch

from PIL import Image
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

from pyramid_oereb.contrib.data_sources.standard.models import get_office, get_document
from pyramid_oereb.contrib.data_sources.standard.sources.document import DatabaseSource
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.document_types import DocumentTypeRecord


@pytest.fixture
def png_image():
    yield Image.new("RGB", (72, 36), (128, 128, 128))


@pytest.fixture
def png_binary(png_image):
    output = io.BytesIO()
    png_image.save(output, format='PNG')
    yield output.getvalue()


@pytest.fixture
def source_params():
    yield {
        "db_connection": "postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db",
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Document"
    }

@pytest.fixture
def office_records():
    yield [
        OfficeRecord(
            {'de': 'Test1'},
            office_at_web={'de': 'www.example1.com'},
            uid='ch99',
            postal_code=4123,
            identifier=1
        ),
        OfficeRecord(
            {'de': 'Test2'},
            office_at_web={'de': 'www.example2.com'},
            uid='ch100',
            postal_code=4321,
            identifier=2
        )
    ]

@pytest.fixture
def document():
    Base = declarative_base()
    Office = get_office(Base, 'test', String)
    Document = get_document(Base, 'test', String, Office)
    yield Document


@pytest.fixture
def date_today():
    yield datetime.date.today()

@pytest.fixture
def all_result_session(session, query, document, date_today, png_binary):
    class Query(query):
        def all(self):
            return [
                document(**{
                    'id': 1,
                    'document_type': 'Hinweis',
                    'index': 1,
                    'law_status': 'inKraft',
                    'title': {'de', 'Titel1'},
                    'office_id': 1,
                    'published_from': date_today - datetime.timedelta(days=5),
                    'published_until': date_today + datetime.timedelta(days=5),
                    'text_at_web': {'de': 'https://test1.abcd'},
                    'abbreviation': {'de': 'abkrz'},
                    'official_number': {'de': 'ch.abc.d123'},
                    'file': png_binary
                }),
                document(**{
                    'id': 2,
                    'document_type': 'Gesetz',
                    'index': 2,
                    'law_status': 'inKraft',
                    'title': {'de', 'Titel2'},
                    'office_id': 1,
                    'published_from': date_today - datetime.timedelta(days=5),
                    'published_until': date_today + datetime.timedelta(days=5),
                    'text_at_web': {'de': 'https://test2.abcd'},
                    'abbreviation': {'de': 'abkrz'},
                    'official_number': {'de': 'ch.abc.d321'},
                    'file': png_binary
                })
            ]
    class Session(session):
        def query(self, term):
            return Query()

    yield Session


@pytest.fixture(autouse=True)
def mock_config_get_main_document_type_by_data_code(app_config):
    def mock_get_main_document_type_by_data_code(doc_type):
        if doc_type == 'Hinweis':
            return DocumentTypeRecord('Hinweis', {'de': 'Hinweis'})
        if doc_type == 'Gesetz':
            return DocumentTypeRecord('Gesetz', {'de': 'Gesetz'})

    with patch('pyramid_oereb.core.config.Config.get_main_document_type_by_data_code', mock_get_main_document_type_by_data_code):
        yield


@pytest.fixture(autouse=True)
def mock_config_get_main_law_status_by_data_code(app_config):
    def mock_get_main_law_status_by_data_code(law_status):
        return DocumentTypeRecord('inKraft', {'de': 'In Kraft'})

    with patch('pyramid_oereb.core.config.Config.get_main_law_status_by_data_code', mock_get_main_law_status_by_data_code):
        yield


def test_read_one(source_params, all_result_session, office_records):
    source = DatabaseSource(**source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_result_session()):
        source.read(office_records)
        assert len(source.records) == 2
        assert isinstance(source.records[0], DocumentRecord)
        assert isinstance(source.records[1], DocumentRecord)
