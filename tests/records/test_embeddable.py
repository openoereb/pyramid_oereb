# -*- coding: utf-8 -*-
import datetime

from pyramid_oereb.lib.records.embeddable import EmbeddableRecord, DatasourceRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.theme import ThemeRecord


def test_embeddable_record_init():
    record = EmbeddableRecord(
        datetime.datetime.now(),
        OfficeRecord({u'de': u'TEST'}),
        OfficeRecord({u'de': u'TEST2'}),
        datetime.datetime.now(),
        []
    )
    assert isinstance(record.cadaster_state, datetime.datetime)
    assert isinstance(record.cadaster_organisation, OfficeRecord)
    assert isinstance(record.data_owner_cadastral_surveying, OfficeRecord)
    assert isinstance(record.datasources, list)


def test_datasource_record():
    record = DatasourceRecord(
        ThemeRecord('Test', {'de': 'Test'}),
        datetime.datetime.now(),
        OfficeRecord({u'de': u'TEST'})
    )
    assert isinstance(record.theme, ThemeRecord)
    assert isinstance(record.date, datetime.datetime)
    assert isinstance(record.owner, OfficeRecord)
