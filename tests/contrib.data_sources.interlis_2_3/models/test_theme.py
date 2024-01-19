from sqlalchemy import Integer, String
from geoalchemy2.types import Geometry as GeoAlchemyGeometry

from pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme import (
    Models, model_factory, model_factory_string_pk, model_factory_integer_pk
)


def test_models(db_connection, schema_name, base):

    office = 'ne.scat'
    document = 'some document object'
    view_service = 'https://www.example.com'
    legend_entry = 1
    public_law_restriction = [{'id': 1, 'type_code': '5b'}, {'id': 2, 'type_code': '3a'}]
    geometry = 'geom'
    public_law_restriction_document = 'a'
    localised_blob = 'blob'
    localised_uri = 'https://www.cadastre.ch/fr'
    multilingual_blob = {'fr': 'blob', 'de': 'blubb, blubb'}
    multilingual_uri = {'de': 'https://www.cadastre.ch/de/home.html',
                        'fr': 'https://www.cadastre.ch/fr/home.html'}

    new_model = Models(office, document, view_service,
                       legend_entry, public_law_restriction, geometry,
                       public_law_restriction_document,
                       localised_blob, localised_uri, multilingual_blob, multilingual_uri,
                       base, db_connection, schema_name
                       )

    assert new_model.Office == 'ne.scat'
    assert new_model.Document == 'some document object'
    assert new_model.ViewService == 'https://www.example.com'
    assert new_model.LegendEntry == 1
    assert isinstance(new_model.PublicLawRestriction, list)
    assert new_model.PublicLawRestriction[1] == {'id': 2, 'type_code': '3a'}
    assert new_model.Geometry == 'geom'
    assert new_model.PublicLawRestrictionDocument == 'a'
    assert new_model.LocalisedBlob == 'blob'
    assert new_model.LocalisedUri == 'https://www.cadastre.ch/fr'
    assert new_model.MultilingualBlob == {'fr': 'blob', 'de': 'blubb, blubb'}
    assert isinstance(new_model.MultilingualUri, dict)
    assert new_model.MultilingualUri['de'] == 'https://www.cadastre.ch/de/home.html'
    assert new_model.Base == base
    assert new_model.db_connection == 'postgresql://mock_user:pass@123.123.123.123:5432/oereb_mock_db'
    assert new_model.schema_name == 'test_schema'


def test_model_factory(db_connection, schema_name, pk_type, srid):

    models = model_factory(
        schema_name,
        pk_type,
        srid,
        db_connection
    )
    assert isinstance(models, Models)
    assert models.db_connection == db_connection
    assert models.PublicLawRestriction.__table_args__['schema'] == schema_name
    assert isinstance(models.PublicLawRestriction.t_id.type, pk_type)
    assert isinstance(models.Geometry.point.type, GeoAlchemyGeometry)
    assert models.Geometry.point.type.geometry_type == 'POINT'
    assert models.Geometry.line.type.geometry_type == 'LINESTRING'
    assert models.Geometry.surface.type.geometry_type == 'POLYGON'
    assert models.Geometry.point.type.srid == srid


def test_model_factory_string_pk(db_connection, schema_name, srid):

    geometry_type = 'POINT'

    models = model_factory_string_pk(
        schema_name,
        geometry_type,
        srid,
        db_connection
    )
    assert isinstance(models.PublicLawRestriction.t_id.type, String)


def test_model_factory_integer_pk(db_connection, schema_name, srid):

    geometry_type = 'POINT'

    models = model_factory_integer_pk(
        schema_name,
        geometry_type,
        srid,
        db_connection
    )
    assert isinstance(models.PublicLawRestriction.t_id.type, Integer)
