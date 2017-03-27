# -*- coding: utf-8 -*-
import datetime
import pytest

from pyramid_oereb.lib.records.documents import Article


def test_get_fields():
    expected_fields = [
            'text_at_web',
            'law_status',
            'published_from',
            'number',
            'text'
        ]
    fields = Article.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        Article()


def test_init():
    record = Article("runningModifications", datetime.date(1985, 8, 29), '125.4')
    assert isinstance(record.law_status, str)
    assert record.text_at_web is None
    assert record.text is None
    assert isinstance(record.number, str)
    assert isinstance(record.published_from, datetime.date)
