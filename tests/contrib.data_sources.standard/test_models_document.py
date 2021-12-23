import pytest
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Date
from sqlalchemy import inspect
from sqlalchemy_utils import JSONType
from pyramid_oereb.contrib.data_sources.standard.models import get_document, get_office

schema_name = 'test'


def test_get_document_mandatory_parameters():
    with pytest.raises(TypeError):
        get_document()


@pytest.mark.parametrize('pk_type,base', [
    (String, declarative_base()),
    (Integer, declarative_base())
])
def test_document_primary_key(pk_type, base):
    office_class = get_office(base, schema_name, pk_type)
    document_class = get_document(base, schema_name, pk_type, office_class)
    inspector = inspect(document_class)

    assert isinstance(inspector.c.id.type, pk_type)
    assert isinstance(inspector.c.office_id.type, pk_type)
    assert inspector.attrs.responsible_office.entity.entity == office_class
    assert inspector.c.id.primary_key


@pytest.mark.parametrize('column_name,column_type,nullable,length', [
    ("document_type", String, False, None),
    ("index", Integer, False, None),
    ("law_status", String, False, None),
    ("title", JSONType, False, None),
    # TODO: Add foreign key testing
    ("published_from", Date, False, None),
    ("published_until", Date, True, None),
    ("text_at_web", JSONType, True, None),
    ("abbreviation", JSONType, True, None),
    ("official_number", JSONType, True, None),
    ("only_in_municipality", Integer, True, None),
    ("file", String, True, None)
])
def test_document_column_values(column_name, column_type, nullable, length):
    base = declarative_base()
    office_class = get_office(base, schema_name, String)
    document_class = get_document(base, schema_name, String, office_class)
    inspector = inspect(document_class)

    assert isinstance(getattr(inspector.c, column_name).type, column_type)
    assert getattr(inspector.c, column_name).nullable == nullable
    if length:
        assert getattr(inspector.c, column_name).type.length == length
