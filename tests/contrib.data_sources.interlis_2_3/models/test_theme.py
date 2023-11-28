import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme import Models


def test_model():

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
    multilingual_uri = {'de': 'https://www.cadastre.ch/de/home.html', 'fr': 'https://www.cadastre.ch/fr/hone.html'}
    base = '???'
    db_connection = 'postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db'
    schema_name = 'my_schema'
    
    new_model = Models(office, document, view_service,
                 legend_entry, public_law_restriction, geometry,
                 public_law_restriction_document,
                 localised_blob, localised_uri, multilingual_blob, multilingual_uri,
                 base, db_connection, schema_name)
    
    assert(new_model.Office == 'ne.scat')
    assert(new_model.Document == 'some document object')
    assert(new_model.ViewService == 'https://www.example.com')
    assert(new_model.LegendEntry == 1)
    assert(isinstance(new_model.PublicLawRestriction, list))
    assert(new_model.PublicLawRestriction[0] == {'id': 1, 'type_code': '5b'})
    assert(new_model.Geometry == 'geom')
    assert(new_model.PublicLawRestrictionDocument == 'a')
    assert(new_model.LocalisedBlob == 'blob')
    assert(new_model.LocalisedUri == 'https://www.cadastre.ch/fr')
    assert(new_model.MultilingualBlob == {'fr': 'blob', 'de': 'blubb, blubb'})
    assert(isinstance(new_model.MultilingualUri, dict))
    assert(new_model.MultilingualUri['de'] == 'https://www.cadastre.ch/de/home.html')
    assert(new_model.Base == '???')
    assert(new_model.db_connection == 'postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db')
    assert(new_model.schema_name == 'my_schema')
