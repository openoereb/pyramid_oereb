import pytest
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, String, Integer
from sqlalchemy import inspect
from pyramid_oereb.contrib.data_sources.standard.models import get_availability

schema_name = 'test'


def test_get_availability_mandatory_parameters():
    with pytest.raises(TypeError):
        get_availability()


@pytest.mark.parametrize('pk_type,base', [
    (String, declarative_base()),
    (Integer, declarative_base())
])
def test_availability_primary_key(pk_type, base):
    availability_class = get_availability(base, schema_name, pk_type)
    inspector = inspect(availability_class)

    assert isinstance(inspector.c.fosnr.type, pk_type)
    assert inspector.c.fosnr.primary_key


@pytest.mark.parametrize('column_name,column_type,nullable,length', [
    ("available", Boolean, False, None)
])
def test_availability_column_values(column_name, column_type, nullable, length):
    base = declarative_base()
    availability_class = get_availability(base, schema_name, String)
    inspector = inspect(availability_class)

    assert isinstance(getattr(inspector.c, column_name).type, column_type)
    assert getattr(inspector.c, column_name).nullable == nullable
    if length:
        assert getattr(inspector.c, column_name).type.length == length
