# -*- coding: utf-8 -*-

import pytest
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DisclaimerRecord()


@pytest.fixture
def record_correct():
    yield DisclaimerRecord({
      "de": "Eigentumsbeschränkungen im Grundbuch",
      "fr": "Restrictions de propriété dans le registre foncier",
      "it": "Restrizioni della proprietà nel re-gistro fondiario",
      "rm": "Restricziuns da la proprietad en il register funsil",
      "en": "Ownership restrictions in the land register"
    }, {
      "de": "Zusätzlich zu den Angaben in diesem Auszug können Eigent...",
      "fr": "Il est possible que des restrictions de propriété fassent...",
      "it": "Oltre alle informazioni contenute nel presente estratto,...",
      "rm": "Supplementarmain a las indicaziuns en quest extract pon r...",
      "en": "In addition to the information contained in this extract,..."
    })


@pytest.fixture
def record_incorrect():
    with pytest.warns(UserWarning):
        yield DisclaimerRecord('title', 'content')


def test_init(record_correct):
    assert isinstance(record_correct.title, dict)
    assert isinstance(record_correct.content, dict)


def test_wrong_types(record_incorrect):
    assert isinstance(record_incorrect.title, str)
    assert isinstance(record_incorrect.content, str)
