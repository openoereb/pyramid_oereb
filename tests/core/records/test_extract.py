# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid.path import DottedNameResolver

from pyramid_oereb.core.records.logo import LogoRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.extract import ExtractRecord
from shapely.geometry.multipolygon import MultiPolygon

from pyramid_oereb.core.records.view_service import ViewServiceRecord


def test_class_variables():
    assert ExtractRecord.electronic_signature is None
    assert ExtractRecord.concerned_theme is None
    assert ExtractRecord.not_concerned_theme is None
    assert ExtractRecord.theme_without_data is None
    assert ExtractRecord.extract_identifier is None


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ExtractRecord()


def create_dummy_extract():
    real_estate = RealEstateRecord(u'test', u'BL', u'Laufen', 2770, 1000, MultiPolygon(), ViewServiceRecord(
        {'de': 'test_link'},
        1,
        1.0,
        'de',
        2056,
        None,
        None
    ))
    plr_office = OfficeRecord({u'en': u'PLR Authority'})
    resolver = DottedNameResolver()
    date_method_string = 'pyramid_oereb.core.hook_methods.get_surveying_data_update_date'  # noqa: E501
    date_method = resolver.resolve(date_method_string)
    update_date_os = date_method(real_estate)
    record = ExtractRecord(
        real_estate,
        LogoRecord('ch', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        LogoRecord('ch.plr', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        LogoRecord('ne', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        LogoRecord('ch.1234', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        plr_office,
        update_date_os
    )
    return record


def test_init(pyramid_oereb_test_config):
    record = create_dummy_extract()
    assert isinstance(record.extract_identifier, str)
    assert isinstance(record.real_estate, RealEstateRecord)
    assert isinstance(record.not_concerned_theme, list)
    assert isinstance(record.concerned_theme, list)
    assert isinstance(record.theme_without_data, list)
    assert isinstance(record.creation_date, datetime.date)
    assert isinstance(record.logo_plr_cadastre, LogoRecord)
    assert isinstance(record.federal_logo, LogoRecord)
    assert isinstance(record.cantonal_logo, LogoRecord)
    assert isinstance(record.municipality_logo, LogoRecord)
    assert isinstance(record.disclaimers, list)
    assert isinstance(record.glossaries, list)
    assert isinstance(record.plr_cadastre_authority, OfficeRecord)
    assert isinstance(record.update_date_os, datetime.datetime)


def test_wrong_types():
    with pytest.warns(UserWarning):
        record = ExtractRecord(
            'real_estate',
            'logo_plr_cadastre',
            'federal_logo',
            'cantonal_logo',
            'municipality_logo',
            'plr_cadastre_authority',
            'update_date_os',
            'disclaimers',
            'glossaries',
            'concerned_theme',
            'not_concerned_theme',
            'theme_without_data',
            'general_information'
        )
    assert isinstance(record.real_estate, str)
    assert isinstance(record.logo_plr_cadastre, str)
    assert isinstance(record.federal_logo, str)
    assert isinstance(record.cantonal_logo, str)
    assert isinstance(record.municipality_logo, str)
    assert isinstance(record.plr_cadastre_authority, str)
    assert isinstance(record.update_date_os, str)
    assert isinstance(record.disclaimers, str)
    assert isinstance(record.glossaries, str)
    assert isinstance(record.concerned_theme, str)
    assert isinstance(record.not_concerned_theme, str)
    assert isinstance(record.theme_without_data, str)
    assert isinstance(record.general_information, str)
