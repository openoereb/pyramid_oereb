# -*- coding: utf-8 -*-
import pytest
import datetime
from pyramid_oereb.lib.records.documents import DocumentBase


def test_get_fields():
    expected_fields = [
        'text_at_web',
        'law_status',
        'published_from'
    ]
    fields = DocumentBase.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentBase()


def test_init():
    record = DocumentBase("runningModifications", datetime.date(1985, 8, 29))
    assert isinstance(record.law_status, str)
    assert record.text_at_web is None
    assert isinstance(record.published_from, datetime.date)
