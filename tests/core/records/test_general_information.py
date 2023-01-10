# -*- coding: utf-8 -*-

import pytest
from pyramid_oereb.core.records.general_information import GeneralInformationRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        GeneralInformationRecord()


def test_init():
    record = GeneralInformationRecord({
        "de": "DEV TEST INFO",
        "fr": "DEV TEST INFO",
        "it": "DEV TEST INFO",
        "rm": "DEV TEST INFO"
    }, {
        "de": "Diese Info soll dazu dienen einen weiteren Textblock zu simulieren u...",
        "fr": "Diese Info soll dazu dienen einen weiteren Textblock zu simulieren u...",
        "it": "Diese Info soll dazu dienen einen weiteren Textblock zu simulieren u...",
        "rm": "Diese Info soll dazu dienen einen weiteren Textblock zu simulieren u..."
    })
    assert isinstance(record.title, dict)
    assert isinstance(record.content, dict)


def test_wrong_types():
    with pytest.warns(UserWarning):
        record = GeneralInformationRecord('titel', 'content')
    assert isinstance(record.title, str)
    assert isinstance(record.content, str)


def test_serialization():
    record = GeneralInformationRecord({
        "de": "DEV TEST INFO"
    }, {
        "de": "Diese Info soll dazu dienen einen weiteren Textblock zu simulieren u..."
    })
    assert isinstance(record.__str__(), str)
