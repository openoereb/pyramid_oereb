# -*- coding: utf-8 -*-

import pytest
from pyramid_oereb.core.records.map_layering import MapLayeringRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        MapLayeringRecord()


def test_init():
    record = MapLayeringRecord(
        'view_service',
        'layer_index',
        'layer_opacity'
    )
    assert isinstance(record.view_service, str)
    assert isinstance(record.layer_index, str)
    assert isinstance(record.layer_opacity, str)
