# -*- coding: utf-8 -*-
import datetime
import pytest

from pyramid_oereb.lib.records.documents import ArticleRecord


def test_get_fields():
    expected_fields = [
        'text_at_web',
        'legal_state',
        'published_from',
        'number',
        'text'
    ]
    fields = ArticleRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ArticleRecord('runningModifications', datetime.date(1985, 8, 29))


def test_init():
    record = ArticleRecord('runningModifications', datetime.date(1985, 8, 29), '125.4')
    assert isinstance(record.legal_state, str)
    assert record.text_at_web is None
    assert record.text is None
    assert isinstance(record.number, str)
    assert isinstance(record.published_from, datetime.date)


def test_to_extract():
    assert ArticleRecord(
        'runningModifications',
        datetime.date(1985, 8, 29),
        '125.4',
        text_at_web='http://article.test.org',
        text='Test'
    ).to_extract() == {
        'legal_state': 'runningModifications',
        'number': '125.4',
        'text_at_web': 'http://article.test.org',
        'text': 'Test'
    }
