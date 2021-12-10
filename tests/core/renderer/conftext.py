import pytest
from unittest.mock import patch

from pyramid_oereb.core.records.real_estate_type import RealEstateTypeRecord
from pyramid_oereb.core.config import Config


@pytest.fixture
def real_estate_test_data(pyramid_oereb_test_config):
    with patch.object(Config, 'real_estate_types', [RealEstateTypeRecord(
            'Liegenschaft',
            {
                "de": "Liegenschaft",
                "fr": "Bien-fonds",
                "it": "Bene immobile",
                "rm": "Bain immobigliar",
                "en": "Property"
            }
    )]):
        yield pyramid_oereb_test_config
