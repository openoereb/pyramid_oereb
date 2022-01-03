# -*- coding: utf-8 -*-

import pytest
from pyramid_oereb.core.records.theme_document import ThemeDocumentRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ThemeDocumentRecord()


def test_init():
    record = ThemeDocumentRecord(
        'theme_id',
        'document_id',
        ['article_numbers']
    )
    assert isinstance(record.theme_id, str)
    assert isinstance(record.document_id, str)
    assert isinstance(record.article_numbers, list)


def test_serialization():
    record = ThemeDocumentRecord(
        'theme_id',
        'document_id',
        ['article_numbers']
    )
    assert isinstance(str(record), str)
