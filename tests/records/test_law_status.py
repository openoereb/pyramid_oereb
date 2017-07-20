# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.law_status import LawStatusRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        LawStatusRecord()


def test_init():
    record = LawStatusRecord(u'inForce', {u'de': u'In Kraft'})
    assert record.code == u'inForce'
    assert isinstance(record.text, dict)
    assert record.text.get('de') == u'In Kraft'


def test_invalid_code():
    with pytest.raises(AttributeError):
        LawStatusRecord(u'inValid', {u'de': u'In Kraft'})


def test_from_config(config):
    assert isinstance(config._config, dict)
    record = LawStatusRecord.from_config(u'inForce')
    assert record.code == u'inForce'
    assert isinstance(record.text, dict)
    assert record.text.get('de')
    assert record.text.get('fr')
    assert record.text.get('it')
    assert record.text.get('rm')
    assert record.text.get('en')

    record = LawStatusRecord.from_config(u'runningModifications')
    assert record.code == u'runningModifications'
    assert isinstance(record.text, dict)
    assert record.text.get('de')
    assert record.text.get('fr')
    assert record.text.get('it')
    assert record.text.get('rm')
    assert record.text.get('en')
