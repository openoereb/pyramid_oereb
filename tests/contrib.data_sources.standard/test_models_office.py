import pytest
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, inspect
from sqlalchemy_utils import JSONType
from pyramid_oereb.contrib.data_sources.standard.models import get_office

schema_name = 'test'


def test_get_office_mandatory_parameters():
    with pytest.raises(TypeError):
        get_office()


@pytest.mark.parametrize('pk_type,base', [
    (String, declarative_base()),
    (Integer, declarative_base())
])
def test_office_primary_key(pk_type, base):
    office_class = get_office(base, schema_name, pk_type)
    inspector = inspect(office_class)

    assert isinstance(inspector.c.id.type, pk_type)
    assert inspector.c.id.primary_key


@pytest.mark.parametrize('column_name,column_type,nullable,length', [
    ("name", JSONType, False, None),
    ("office_at_web", JSONType, True, None),
    ("uid", String, True, 12),
    ("line1", String, True, None),
    ("line2", String, True, None),
    ("street", String, True, None),
    ("number", String, True, None),
    ("postal_code", Integer, True, None),
    ("city", String, True, None)
])
def test_document_column_values(column_name, column_type, nullable, length):
    base = declarative_base()
    office_class = get_office(base, schema_name, String)
    inspector = inspect(office_class)

    assert isinstance(getattr(inspector.c, column_name).type, column_type)
    assert getattr(inspector.c, column_name).nullable == nullable
    if length:
        assert getattr(inspector.c, column_name).type.length == length
