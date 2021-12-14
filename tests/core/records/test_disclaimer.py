# -*- coding: utf-8 -*-

import pytest
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DisclaimerRecord()


def test_init():
    record = DisclaimerRecord({
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
    assert isinstance(record.title, dict)
    assert isinstance(record.content, dict)

def test_wrong_types():
    record = DisclaimerRecord('titel', 'content')
    assert isinstance(record.title, str)
    assert isinstance(record.content, str)
