# -*- coding: utf-8 -*-
import datetime

from pyramid_oereb.lib.records.embeddable import EmbeddableRecord, TransferFromSourceRecord
from pyramid_oereb.lib.records.office import OfficeRecord


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
    assert isinstance(record.data_sources, list)


def test_source_record():
    record = TransferFromSourceRecord(
        datetime.datetime.now(),
        OfficeRecord({u'de': u'TEST'})
    )
    assert isinstance(record.date, datetime.datetime)
    assert isinstance(record.owner, OfficeRecord)
