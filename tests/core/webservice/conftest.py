import pytest
from unittest.mock import patch
# from pyramid_oereb.core import b64
from pyramid_oereb.core.adapter import FileAdapter

# from datetime import date, timedelta

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.municipality import MunicipalityRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.logo import LogoRecord
from pyramid_oereb.core.records.real_estate_type import RealEstateTypeRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord


file_adapter = FileAdapter()


@pytest.fixture
def extract_real_estate_data(real_estate_data, municipalities, themes, real_estate_types_test_data):
    pass


@pytest.fixture(autouse=True)
def municipalities(pyramid_oereb_test_config):
    with patch(
            'pyramid_oereb.core.config.Config.municipalities',
            [MunicipalityRecord(1234, 'test', True)]
    ):
        yield pyramid_oereb_test_config


@pytest.fixture
def address(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models import main

    # Add dummy address
    addresses = [main.Address(**{
        'street_name': u'test',
        'street_number': u'10',
        'zip_code': 4410,
        'geom': 'SRID=2056;POINT(1 1)'
    })]
    dbsession.add_all(addresses)


@pytest.fixture
def real_estate_types_test_data(pyramid_oereb_test_config):
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


@pytest.fixture
def logos(pyramid_oereb_test_config):
    with patch.object(Config, 'logos', [
            LogoRecord('ch', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ch.plr', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ne', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ch.1234', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
    ]):
        yield pyramid_oereb_test_config


@pytest.fixture
def themes(pyramid_oereb_test_config):
    with patch.object(Config, 'themes', [
            ThemeRecord(**{
                'code': 'ch.Nutzungsplanung',
                'sub_code': None,
                'title': {"de": "Nutzungsplanung (kantonal/kommunal)",
                          "fr": "Plans d’affectation (cantonaux/communaux)",
                          "it": "Piani di utilizzazione (cantonali/comunali)",
                          "rm": "Planisaziun d''utilisaziun (chantunal/communal)",
                          "en": "Land use plans (cantonal/municipal)"},
                'extract_index': 20
            }),
            ThemeRecord(**{
                'code': 'ch.StatischeWaldgrenzen',
                'title': {"de": "Statische Waldgrenzen",
                          "fr": "Limites forestières statiques",
                          "it": "Margini statici della foresta",
                          "rm": "Cunfins statics dal guaud",
                          "en": "Static forest perimeters"},
                'extract_index': 710
            }),
            ThemeRecord(**{
                'code': 'ch.ProjektierungszonenNationalstrassen',
                'title': {"de": "Projektierungszonen Nationalstrassen",
                          "fr": "Zones réservées des routes nationales",
                          "it": "Zone riservate per le strade nazionali",
                          "rm": "Zonas da projectaziun da las vias naziunalas",
                          "en": "Reserved zones for motorways"},
                'extract_index': 110
            }),
            ThemeRecord(**{
                'code': 'ch.BelasteteStandorte',
                'title': {"de": "Kataster der belasteten Standorte",
                          "fr": "Cadastre des sites pollués",
                          "it": "Catasto dei siti inquinati",
                          "rm": "Cataster dals lieus contaminads",
                          "en": "Cadastre of contaminated sites"},
                'extract_index': 410
            }),
    ]):
        yield pyramid_oereb_test_config


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
