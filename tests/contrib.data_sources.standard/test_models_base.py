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


def test_office_column_values():
    office_class = get_office(declarative_base(), schema_name, String)
    inspector = inspect(office_class)

    assert isinstance(inspector.c.name.type, JSONType)
    assert not inspector.c.name.nullable

    assert isinstance(inspector.c.office_at_web.type, JSONType)
    assert inspector.c.office_at_web.nullable

    assert isinstance(inspector.c.uid.type, String)
    assert inspector.c.uid.type.length == 12
    assert inspector.c.uid.nullable

    assert isinstance(inspector.c.line1.type, String)
    assert inspector.c.line1.nullable

    assert isinstance(inspector.c.line2.type, String)
    assert inspector.c.line2.nullable

    assert isinstance(inspector.c.street.type, String)
    assert inspector.c.street.nullable

    assert isinstance(inspector.c.number.type, String)
    assert inspector.c.number.nullable

    assert isinstance(inspector.c.postal_code.type, Integer)
    assert inspector.c.postal_code.nullable

    assert isinstance(inspector.c.city.type, String)
    assert inspector.c.city.nullable
