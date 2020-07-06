# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib.records.glossary import GlossaryRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        GlossaryRecord()


def test_init():
    record = GlossaryRecord({'fr': u'SGRF'}, {'fr': u'Service de la géomatique et du registre foncier'})
    assert record.title.get('fr') == u'SGRF'
    assert record.content is not None
    assert isinstance(record.content.get('fr'), str)
