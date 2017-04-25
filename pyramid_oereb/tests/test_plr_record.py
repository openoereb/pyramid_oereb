# -*- coding: utf-8 -*-
import datetime
import pytest
from shapely.geometry import Point

from pyramid_oereb.lib.records.documents import DocumentRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord, ViewServiceRecord


def test_get_fields():
    expected_fields = [
        'topic',
        'documents',
        'geometries',
        'view_service',
        'refinements',
        'additional_topic',
        'content',
        'type_code_list',
        'type_code',
        'basis',
        'published_from',
        'legal_state',
        'subtopic',
        'responsible_office'
    ]
    fields = PlrRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        PlrRecord()


def test_init():
    office = OfficeRecord('Office')
    record = PlrRecord('Topic', 'Content', 'runningModifications', datetime.date(1985, 8, 29), office)
    assert record.content == 'Content'
    assert record.subtopic is None
    assert isinstance(record.geometries, list)
    assert isinstance(record.responsible_office, OfficeRecord)


def test_to_extract():
    office = OfficeRecord('Office')
    legends = [
        LegendEntryRecord(bin(100), 'test1', 'test1_code', 'test1', 'test1'),
        LegendEntryRecord(bin(100), 'test2', 'test2_code', 'test2', 'test2')
    ]
    view_service = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch', legends)
    document = DocumentRecord('runningModifications', datetime.date(1985, 8, 29), u'Document', office)
    point = Point((0, 0))
    geometry = GeometryRecord('runningModifications', datetime.date(1985, 8, 29), geom=point, office=office)
    plr_record = PlrRecord('Topic', 'Content', 'runningModifications', datetime.date(1985, 8, 29), office,
                           type_code='test1_code', view_service=view_service, documents=[document],
                           geometries=[geometry])
    assert plr_record.to_extract() == {
        'affected': True,
        'content': 'Content',
        'topic': 'Topic',
        'legal_state': 'runningModifications',
        'type_code': 'test1_code',
        'responsible_office': {
            'name': 'Office'
        },
        'view_service': {
            'link_wms': 'http://www.test.url.ch',
            'legend_web': 'http://www.test.url.ch',
            'legends': [
                {
                    'symbol': bin(100),
                    'legend_text': 'test1',
                    'type_code': 'test1_code',
                    'type_code_list': 'test1',
                    'theme': 'test1'
                }
            ]
        },
        'documents': [
            {
                'legal_state': 'runningModifications',
                'title': 'Document',
                'responsible_office': {
                    'name': 'Office'
                }
            }
        ],
        'geometries': [
            {
                'legal_state': 'runningModifications',
                'geom': point.wkt,
                'office': {
                    'name': 'Office'
                }
            }
        ]
    }
