# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ExclusionOfLiabilityRecord()


def test_init():
    record = ExclusionOfLiabilityRecord(title='Disclaimer', content=u'No warranty on nothing.')
    assert record.title == 'Disclaimer'
    assert record.content is not None
    assert isinstance(record.content, unicode)
