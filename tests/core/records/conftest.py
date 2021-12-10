import pytest
from unittest.mock import patch

from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.config import Config


@pytest.fixture
def law_test_data(pyramid_oereb_test_config):
    with patch.object(Config, 'law_status', [LawStatusRecord(
            'inKraft',
            {
                "de": "Rechtskräftig",
                "fr": "En vigueur",
                "it": "In vigore",
                "rm": "En vigur",
                "en": "In force"
            }
    )]):
        yield pyramid_oereb_test_config


