import pytest
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer
from pyramid_oereb.contrib.data_sources.standard.models import get_office

Base = declarative_base()
schema_name = 'test'


def test_get_office_mandatory_parameters():
    with pytest.raises(TypeError):
        get_office()

def test_get_office():
    office_class = get_office(Base, schema_name, String)
    assert isinstance(office_class().id, str)
