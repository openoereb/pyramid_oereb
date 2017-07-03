# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.law_status import LawStatusRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        LawStatusRecord()


def test_init():
    record = LawStatusRecord('inForce')
    assert record.code == 'inForce'
    assert isinstance(record.text, dict)
