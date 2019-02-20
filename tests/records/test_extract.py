# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid.path import DottedNameResolver

from pyramid_oereb import Config
from pyramid_oereb.lib.records.embeddable import EmbeddableRecord, DatasourceRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from shapely.geometry.multipolygon import MultiPolygon

from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


def test_class_variables():
    assert ExtractRecord.electronic_signature is None
    assert ExtractRecord.concerned_theme is None
    assert ExtractRecord.not_concerned_theme is None
    assert ExtractRecord.theme_without_data is None
    assert ExtractRecord.extract_identifier is None
    assert ExtractRecord.qr_code is None


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ExtractRecord()


def test_init():
    date = datetime.datetime.now()
    real_estate = RealEstateRecord(u'test', u'BL', u'Laufen', 2770, 1000, MultiPolygon(), ViewServiceRecord(
        'test_link',
        1,
        1.0,
        {'de': 'test_legend'}
    ))
    plr_office = OfficeRecord({u'en': u'PLR Authority'})
    resolver = DottedNameResolver()
    date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
    date_method = resolver.resolve(date_method_string)
    av_update_date = date_method(real_estate)
    base_data = Config.get_base_data(av_update_date)

    av_provider_method_string = Config.get('extract').get('base_data').get('methods').get('provider')
    av_provider_method = resolver.resolve(av_provider_method_string)
    cadaster_state = date
    theme = ThemeRecord(u'TEST', {u'de': u'TEST TEXT'})
    datasources = [DatasourceRecord(theme, date, plr_office)]
    plr_cadastre_authority = Config.get_plr_cadastre_authority()
    embeddable = EmbeddableRecord(
        cadaster_state,
        plr_cadastre_authority,
        av_provider_method(real_estate),
        av_update_date,
        datasources
    )
    record = ExtractRecord(
        real_estate,
        ImageRecord('100'.encode('utf-8')),
        ImageRecord('100'.encode('utf-8')),
        ImageRecord('100'.encode('utf-8')),
        ImageRecord('100'.encode('utf-8')),
        plr_office,
        base_data,
        embeddable
    )
    assert isinstance(record.extract_identifier, str)
    assert isinstance(record.real_estate, RealEstateRecord)
    assert isinstance(record.not_concerned_theme, list)
    assert isinstance(record.concerned_theme, list)
    assert isinstance(record.theme_without_data, list)
    assert isinstance(record.creation_date, datetime.date)
    assert isinstance(record.logo_plr_cadastre, ImageRecord)
    assert isinstance(record.federal_logo, ImageRecord)
    assert isinstance(record.cantonal_logo, ImageRecord)
    assert isinstance(record.municipality_logo, ImageRecord)
    assert isinstance(record.exclusions_of_liability, list)
    assert isinstance(record.glossaries, list)
    assert isinstance(record.plr_cadastre_authority, OfficeRecord)
    assert isinstance(record.base_data, dict)
    assert isinstance(record.embeddable, EmbeddableRecord)
