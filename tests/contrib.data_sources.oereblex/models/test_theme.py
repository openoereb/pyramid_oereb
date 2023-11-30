
from sqlalchemy import Integer, String

from pyramid_oereb.contrib.data_sources.oereblex.models.theme import (
    Models, model_factory, model_factory_string_pk, model_factory_integer_pk
)


def test_models():
    models = Models(
        'office',
        'view_service',
        'legend_entry',
        'public_law_restriction',
        'geometry',
        'base',
        'db_connection',
        'schema_name'
    )
    assert models.Office == 'office'
    assert models.ViewService == 'view_service'
    assert models.LegendEntry == 'legend_entry'
    assert models.PublicLawRestriction == 'public_law_restriction'
    assert models.Geometry == 'geometry'
    assert models.Base == 'base'
    assert models.db_connection == 'db_connection'
    assert models.schema_name == 'schema_name'


def test_model_factory(db_connection):
    srid = 2056
    geometry_type = 'POINT'
    pk_type = Integer
    schema_name = 'test'

    models = model_factory(
        schema_name,
        pk_type,
        geometry_type,
        srid,
        db_connection
    )
    assert isinstance(models, Models)
    assert models.db_connection == db_connection
    assert models.PublicLawRestriction.__table_args__['schema'] == schema_name
    assert isinstance(models.PublicLawRestriction.id.type, pk_type)
    assert models.Geometry.geom.type.geometry_type == geometry_type
    assert models.Geometry.geom.type.srid == srid


def test_model_factory_string_pk(db_connection):
    srid = 2056
    geometry_type = 'POINT'
    schema_name = 'test'
    models = model_factory_string_pk(
        schema_name,
        geometry_type,
        srid,
        db_connection
    )
    assert isinstance(models.PublicLawRestriction.id.type, String)


def test_model_factory_integer_pk(db_connection):
    srid = 2056
    geometry_type = 'POINT'
    schema_name = 'test'
    models = model_factory_integer_pk(
        schema_name,
        geometry_type,
        srid,
        db_connection
    )
    assert isinstance(models.PublicLawRestriction.id.type, Integer)
