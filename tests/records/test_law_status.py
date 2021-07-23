# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.config import Config


def test_mandatory_fields():
    with pytest.raises(TypeError):
        LawStatusRecord()


def test_init():
    record = LawStatusRecord(u'inKraft', {u'de': u'In Kraft'})
    assert record.code == u'inKraft'
    assert isinstance(record.text, dict)
    assert record.text.get('de') == u'In Kraft'


def test_invalid_code():
    with pytest.raises(AttributeError):
        LawStatusRecord(u'inValid', {u'de': u'In Kraft'})


def test_from_config():
    record = Config.get_law_status_by_law_status_code(u'inKraft')
    assert record.code == u'inKraft'
    assert isinstance(record.text, dict)
    assert record.text.get('de')
    assert record.text.get('fr')
    assert record.text.get('it')
    assert record.text.get('rm')
    assert record.text.get('en')

    record = Config.get_law_status_by_law_status_code(u'runningModifications')
    assert record.code == u'runningModifications'
    assert isinstance(record.text, dict)
    assert record.text.get('de')
    assert record.text.get('fr')
    assert record.text.get('it')
    assert record.text.get('rm')
    assert record.text.get('en')
