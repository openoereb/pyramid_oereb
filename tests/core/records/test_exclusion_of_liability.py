# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.core.records.disclaimer import DisclaimerRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DisclaimerRecord()


def test_init():
    record = DisclaimerRecord({'en': 'Disclaimer'}, {'en': u'No warranty on nothing.'})
    assert record.title.get('en') == 'Disclaimer'
    assert record.content is not None
    assert isinstance(record.content.get('en'), str)
