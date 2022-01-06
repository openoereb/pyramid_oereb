# -*- coding: utf-8 -*-

import pytest
from pyramid_oereb.core.records.availability import AvailabilityRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        AvailabilityRecord()


def test_init():
    record = AvailabilityRecord(2771, True)
    assert isinstance(record.fosnr, int)
    assert isinstance(record.available, bool)
