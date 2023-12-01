# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.exc import ProgrammingError

from unittest.mock import patch

from pyramid.config import ConfigurationError

# from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.readers.theme import ThemeReader
from pyramid_oereb.core.readers.theme_document import ThemeDocumentReader
from pyramid_oereb.core.readers.general_information import GeneralInformationReader
from pyramid_oereb.core.readers.law_status import LawStatusReader
from pyramid_oereb.core.readers.document import DocumentReader
from pyramid_oereb.core.readers.office import OfficeReader
from pyramid_oereb.core.readers.availability import AvailabilityReader
from pyramid_oereb.core.readers.glossary import GlossaryReader
from pyramid_oereb.core.readers.disclaimer import DisclaimerReader
from pyramid_oereb.core.readers.municipality import MunicipalityReader
from pyramid_oereb.core.readers.logo import LogoReader
from pyramid_oereb.core.readers.document_types import DocumentTypeReader
from pyramid_oereb.core.readers.real_estate_type import RealEstateTypeReader
from pyramid_oereb.core.readers.map_layering import MapLayeringReader
from pyramid_oereb.core.records.availability import AvailabilityRecord
from pyramid_oereb.core.records.municipality import MunicipalityRecord


# order=-1 to run them after all and don't screw the configuration in Config
@pytest.mark.run(order=-1)
def test_missing_configuration_file():
    Config._config = None
    with pytest.raises(ConfigurationError):
        Config.init(None, None)


@pytest.mark.run(order=-1)
def test_missing_configuration_section():
    Config._config = None
    with pytest.raises(ConfigurationError):
        Config.init('myconfig.yml', None)


@pytest.mark.run(order=-1)
def test_wrong_configuration_section(config_path):
    Config._config = None
    with pytest.raises(ConfigurationError):
        Config.init(config_path, 'invalidsection')


@pytest.mark.run(order=-1)
def test_configuration_file_not_found():
    Config._config = None
    with pytest.raises(IOError) as excinfo:
        Config.init('not_existing_config.yml', 'invalidsection')
    assert ', Current working directory is ' in str(excinfo.value)


@pytest.mark.run(order=-1)
def test_parse_configuration(config_path):
    Config._config = None
    Config.init(config_path, 'section2')
    assert Config.get('param1') == 1
    assert len(Config.get('param2')) == 2
    assert Config.get('param2')[0] == 'first'
    assert Config.get('param2')[1] == 'second'


@pytest.mark.run(order=-1)
def test_get_plr_cadastre_authority(config_path):
    Config._config = None
    Config.init(config_path, 'pyramid_oereb')
    plr_cadastre_authority = Config.get_plr_cadastre_authority()
    assert isinstance(plr_cadastre_authority, OfficeRecord)


@pytest.mark.run(order=-1)
def test_get_logo_config(config_path):
    Config._config = None
    Config.init(config_path, 'pyramid_oereb')
    logo_config = Config.get_logo_config()
    assert isinstance(logo_config, dict)
    source = logo_config.get('source')
    assert isinstance(source, dict)
    class_config = source.get('class')
    assert isinstance(class_config, str)
    params = source.get('params')
    assert isinstance(params, dict)
    db_connection = params.get('db_connection')
    assert isinstance(db_connection, str)
    model = params.get('model')
    assert isinstance(model, str)


@pytest.mark.run(order=-1)
def test_init_logos():
    with patch.object(Config, '_read_logos', return_value=['logo2', 'logo3']):
        Config._config = None
        Config.init_logos()
        assert len(Config.logos) == 2


@pytest.mark.run(order=-1)
def test_init_logos_error():
    def mock_read_logos():
        raise ProgrammingError('a', 'b', 'c')

    with patch.object(Config, '_read_logos', mock_read_logos):
        Config._config = None
        Config.init_logos()
        assert Config.logos is None


@pytest.mark.parametrize('test_logos_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.logo.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Logo"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.logo.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Logo"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_logos(test_logos_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_logo_config', return_value=test_logos_config):
        with patch.object(LogoReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_logos()) == expected_result


@pytest.mark.run(order=-1)
def test_read_logos_config_none():
    Config._config = None
    with patch.object(Config, 'get_logo_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_logos()


@pytest.mark.run(order=-1)
def test_get_logo_hooks():
    with patch.object(Config, 'get_logo_config', return_value={"hooks": []}):
        Config._config = None
        assert Config.get_logo_hooks() == []


@pytest.mark.parametrize('test_value', [
    ({"logos": [{"hooks": []}]}),
    ({"logos": [{"not_expecting_key": []}]}),
    (None)
])
@pytest.mark.run(order=-1)
def test_get_logo_hooks_none(test_value):
    with patch.object(Config, 'get_logo_config', return_value=test_value):
        Config._config = None
        with pytest.raises(ConfigurationError):
            Config.get_logo_hooks()


@pytest.mark.run(order=-1)
def test_get_all_federal(config_path):
    Config._config = None
    Config.init(config_path, 'pyramid_oereb')
    all_federal = Config.get_all_federal()
    assert isinstance(all_federal, list)
    assert len(all_federal) == 2
    assert 'ch.BelasteteStandorte' in all_federal


@pytest.mark.run(order=-1)
def test_get_oereblex_config(config_path):
    Config._config = None
    Config.init(config_path, 'pyramid_oereb')
    cfg = Config.get_oereblex_config()
    assert isinstance(cfg, dict)
    assert cfg == {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'proxy': {
            'http': 'http://my.proxy.org',
            'https': None
        }
    }


@pytest.mark.run(order=-1)
def test_get_real_estate_main_page_config(config_path):
    Config._config = None
    Config.init(config_path, 'pyramid_oereb')
    lang = Config.get('default_language')
    plan_for_land_register_main_page_config = Config.get_plan_for_land_register_main_page_config()
    assert plan_for_land_register_main_page_config.get('reference_wms')[lang] == (
        'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&'
        'STYLES=default&CRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&'
        'WIDTH=493&HEIGHT=280&FORMAT=image/png&LAYERS=ch.swisstopo-vd.amtliche-vermessung'
    )
    assert plan_for_land_register_main_page_config.get('layer_index') == 2
    assert plan_for_land_register_main_page_config.get('layer_opacity') == 0.5


@pytest.mark.parametrize('test_theme,expected_result', [
    ({'theme': 'params_dict'}, 'params_dict'),
    ({'wrong_key': {}}, None)
    ])
@pytest.mark.run(order=-1)
def test_get_theme_config(test_theme, expected_result):
    Config._config = None
    Config._config = test_theme
    assert Config.get_theme_config() == expected_result


@pytest.mark.run(order=-1)
def test_get_theme_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_theme_config()


@pytest.mark.parametrize(
        'test_theme_config,test_theme_code,expected_result',
        [({'plrs': [{'code': 'ch.Nutzungsplanung'}]}, 'ch.Nutzungsplanung', {'code': 'ch.Nutzungsplanung'}),
         ({'plrs': [{'code': 'ch.Nutzungsplanung'}]}, 'ch.Ne.Baulinien', None),
         ({}, 'ch.Ne.Baulinien', None)])
@pytest.mark.run(order=-1)
def test_get_theme_config_by_code(test_theme_config, test_theme_code, expected_result):
    with patch.object(Config, '_config', test_theme_config):
        assert Config.get_theme_config_by_code(test_theme_code) == expected_result


@pytest.mark.run(order=-1)
def test_get_theme_config_by_code_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_theme_config_by_code('ch.NE.Baulinien')


@pytest.mark.parametrize('test_themes_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.theme.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Theme"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.theme.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Theme"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_themes(test_themes_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_theme_config', return_value=test_themes_config):
        with patch.object(ThemeReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_themes()) == expected_result


@pytest.mark.run(order=-1)
def test_read_themes_config_none():
    Config._config = None
    with patch.object(Config, 'get_theme_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_themes()


@pytest.mark.parametrize('test_theme_document_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.theme_document.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.ThemeDocument"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.theme_document.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.ThemeDocument"
            }
        }
    }, 1)
    ])
@pytest.mark.run(order=-1)
def test_read_theme_document(test_theme_document_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_theme_document_config', return_value=test_theme_document_config):
        with patch.object(ThemeDocumentReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_theme_document()) == expected_result


@pytest.mark.run(order=-1)
def test_read_theme_document_config_none():
    Config._config = None
    with patch.object(Config, 'get_theme_document_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_theme_document()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'real_estate_type': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_real_estate_type_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_real_estate_type_config() == expected_value


@pytest.mark.parametrize('test_value,expected_result', [
    ({'real_estate': {}}, {}),
    ({'not_the_expected_real_estate_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_real_estate_config(test_value, expected_result):
    Config._config = test_value
    assert Config.get_real_estate_config() == expected_result


@pytest.mark.run(order=-1)
def test_get_real_estate_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_real_estate_config()


@pytest.mark.run(order=-1)
def test_get_real_estate_type_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_real_estate_type_config()


@pytest.mark.run(order=-1)
def test_get_real_estate_type_lookups():
    with patch.object(Config, 'get_real_estate_type_config', return_value={"lookup": {}}):
        assert Config.get_real_estate_type_lookups() == {}


@pytest.mark.run(order=-1)
def test_get_real_estate_type_lookups_none():
    with patch.object(Config, 'get_real_estate_type_config', return_value={}):
        with pytest.raises(ConfigurationError):
            Config.get_real_estate_type_lookups()


@pytest.fixture
def patch_config_get_theme_config_by_code(return_value):
    def config_get_theme_config_by_code(theme_code):
        return return_value
    with patch.object(
            Config, 'get_theme_config_by_code',
            config_get_theme_config_by_code):
        yield


@pytest.mark.run(order=-1)
def test_get_document_types_lookups():
    with patch.object(Config, 'get_theme_config_by_code', return_value={"document_types_lookup": [{}]}):
        result = Config.get_document_types_lookups('ch.Nutzungsplanung')
        assert result == [{}]


@pytest.mark.run(order=-1)
def test_get_document_types_lookups_raises_error():
    with patch.object(Config, 'get_theme_config_by_code', return_value={}):
        with pytest.raises(ConfigurationError):
            Config.get_document_types_lookups('ch.Nutzungsplanung')


@pytest.mark.parametrize('test_value, expected_results', [
    ({'glossary': {}}, {}),
    ({'not_te_excpected_glossary_key': {}}, None)
    ])
@pytest.mark.run(order=-1)
def test_get_glossary_config(test_value, expected_results):
    Config._config = test_value
    assert Config.get_glossary_config() == expected_results


@pytest.mark.run(order=-1)
def test_get_glossary_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_glossary_config()


@pytest.mark.parametrize('test_value,expected_result', [
    ({'law_status_labels': {}}, {}),
    ({'not_the_expected_law_status_labels_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_law_status_config(test_value, expected_result):
    Config._config = test_value
    assert Config.get_law_status_config() == expected_result


@pytest.mark.run(order=-1)
def test_get_law_status_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_law_status_config()


@pytest.mark.parametrize('test_value,expected_result', [

    ({'extract': {}}, {}),
    ({'not_the_expected_extract_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_extract_config(test_value, expected_result):
    Config._config = test_value
    assert Config.get_extract_config() == expected_result


@pytest.mark.run(order=-1)
def test_get_extract_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_extract_config()


@pytest.mark.parametrize('test_general_information_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.general_information.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.GeneralInformation"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.general_information.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.GeneralInformation"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_general_information(test_general_information_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_info_config', return_value=test_general_information_config):
        with patch.object(GeneralInformationReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_general_information()) == expected_result


@pytest.mark.run(order=-1)
def test_read_general_information_config_none():
    Config._config = None
    with patch.object(Config, 'get_info_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_general_information()


@pytest.mark.parametrize('test_law_status_config,expected_result', [
    ({
        "source": {
            "class":
            "pyramid_oereb.contrib.data_sources.standard.sources.law_status.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.LawStatus"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.law_status.DatabaseSource",
            "params": {
              "db_connection": "*main_db_connection",
              "model": "pyramid_oereb.contrib.data_sources.standard.models.main.LawStatus"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_law_status(test_law_status_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_law_status_config', return_value=test_law_status_config):
        with patch.object(LawStatusReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_law_status()) == expected_result


@pytest.mark.run(order=-1)
def test_read_law_status_config_none():
    Config._config = None
    with patch.object(Config, 'get_law_status_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_law_status()


@pytest.mark.parametrize('test_documents_config,expected_result', [
    ({
        "source": {
            "class":
            "pyramid_oereb.contrib.data_sources.standard.sources.document.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Document"
            }
        }
    }, 0),
    ({
        "source": {
            "class":
            "pyramid_oereb.contrib.data_sources.standard.sources.document.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Document"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_documents(test_documents_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_document_config', return_value=test_documents_config):
        with patch.object(DocumentReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_documents()) == expected_result


@pytest.mark.run(order=-1)
def test_read_documents_config_none():
    Config._config = None
    with patch.object(Config, 'get_document_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_documents()


@pytest.mark.parametrize('test_offices_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.office.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Office"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.office.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Office"
            }
        }
    }, 1),
])
@pytest.mark.run(order=-1)
def test_read_offices(test_offices_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_office_config', return_value=test_offices_config):
        with patch.object(OfficeReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_offices()) == expected_result


@pytest.mark.run(order=-1)
def test_read_offices_config_none():
    Config._config = None
    with patch.object(Config, 'get_office_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_offices()


@pytest.mark.parametrize('test_availability_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.availability.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Availability"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.availability.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Availability"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_availabilities(test_availability_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_availability_config', return_value=test_availability_config):
        with patch.object(AvailabilityReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_availabilities()) == expected_result


@pytest.mark.run(order=-1)
def test_read_availabilities_config_none():
    Config._config = None
    with patch.object(Config, 'get_availability_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_availabilities()


@pytest.mark.parametrize('test_glossary_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.glossary.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Glossary"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.glossary.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Glossary"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_glossaries(test_glossary_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_glossary_config', return_value=test_glossary_config):
        with patch.object(GlossaryReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_glossaries()) == expected_result


@pytest.mark.run(order=-1)
def test_read_glossaries_config_none():
    Config._config = None
    with patch.object(Config, 'get_glossary_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_glossaries()


@pytest.mark.parametrize('test_disclaimer_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.disclaimer.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Disclaimer"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.disclaimer.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Disclaimer"
            }
        }
    }, 1),
])
@pytest.mark.run(order=-1)
def test_read_disclaimers(test_disclaimer_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_disclaimer_config', return_value=test_disclaimer_config):
        with patch.object(DisclaimerReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_disclaimers()) == expected_result


@pytest.mark.run(order=-1)
def test_read_disclaimers_config_none():
    Config._config = None
    with patch.object(Config, 'get_disclaimer_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_disclaimers()


@pytest.mark.parametrize('test_municipality_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.municipality.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Municipality"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.municipality.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Municipality"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_municipalities(test_municipality_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_municipality_config', return_value=test_municipality_config):
        with patch.object(MunicipalityReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_municipalities()) == expected_result


@pytest.mark.run(order=-1)
def test_read_municipalities_config_none():
    Config._config = None
    with patch.object(Config, 'get_municipality_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_municipalities()


@pytest.mark.parametrize('test_document_types_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.document_types.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.DocumentTypeText"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.document_types.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.DocumentTypeText"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_document_types(test_document_types_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_document_types_config', return_value=test_document_types_config):
        with patch.object(DocumentTypeReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_document_types()) == expected_result


@pytest.mark.run(order=-1)
def test_read_document_types_config_none():
    Config._config = None
    with patch.object(Config, 'get_document_types_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_document_types()


@pytest.mark.parametrize('test_real_estate_type_config,expected_result', [
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.real_estate_type.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.RealEstateType"
            }
        }
    }, 0),
    ({
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.real_estate_type.DatabaseSource",
            "params": {
                "db_connection": "*main_db_connection",
                "model": "pyramid_oereb.contrib.data_sources.standard.models.main.RealEstateType"
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_real_estate_types(test_real_estate_type_config, expected_result):
    Config._config = None
    with patch.object(Config, 'get_real_estate_type_config', return_value=test_real_estate_type_config):
        with patch.object(RealEstateTypeReader, 'read', return_value=[None] * expected_result):
            assert len(Config._read_real_estate_types()) == expected_result


@pytest.mark.run(order=-1)
def test_read_real_estate_types_config_none():
    Config._config = None
    with patch.object(Config, 'get_real_estate_type_config', return_value=None):
        with pytest.raises(ConfigurationError):
            Config._read_real_estate_types()


@pytest.mark.parametrize('test_map_layering_config,expected_result', [
    ({
        "map_layering": {
            "source": {
                "class": "pyramid_oereb.contrib.data_sources.standard.sources.map_layering.DatabaseSource",
                "params": {
                    "db_connection": "*main_db_connection",
                    "model": "pyramid_oereb.contrib.data_sources.standard.models.main.MapLayering"
                }
            }
        }
    }, 0),
    ({
        "map_layering": {
            "source": {
                "class": "pyramid_oereb.contrib.data_sources.standard.sources.map_layering.DatabaseSource",
                "params": {
                    "db_connection": "*main_db_connection",
                    "model": "pyramid_oereb.contrib.data_sources.standard.models.main.MapLayering"
                }
            }
        }
    }, 1)
])
@pytest.mark.run(order=-1)
def test_read_map_layering(test_map_layering_config, expected_result):
    Config._config = None
    Config._config = test_map_layering_config
    with patch.object(MapLayeringReader, 'read', return_value=[None] * expected_result):
        assert len(Config._read_map_layering()) == expected_result


@pytest.mark.run(order=-1)
def test_read_map_layering_config_none():
    Config._config = {}
    with pytest.raises(ConfigurationError):
        Config._read_map_layering()


@pytest.mark.run(order=1)
def test_init_availabilities():
    Config._config = None
    with patch.object(Config, '_read_availabilities', return_value=""):
        assert Config.availabilities is None
        Config.init_availabilities()
        assert Config.availabilities == ""


@pytest.mark.run(order=1)
def test_init_availabilities_error():
    def mock_read_availabilities():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_availabilities', mock_read_availabilities):
        Config._config = None
        Config.init_availabilities()
        assert Config.availabilities is None


@pytest.mark.run(order=1)
def test_init_glossaries():
    Config._config = None
    with patch.object(Config, '_read_glossaries', return_value=""):
        assert Config.glossaries is None
        Config.init_glossaries()
        assert Config.glossaries == ""


@pytest.mark.run(order=1)
def test_init_glossaries_error():
    def mock_read_glossaries():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_glossaries', mock_read_glossaries):
        Config._config = None
        Config.init_glossaries()
        assert Config.glossaries is None


@pytest.mark.run(order=1)
def test_init_disclaimers():
    Config._config = None
    with patch.object(Config, '_read_disclaimers', return_value=""):
        assert Config.disclaimers is None
        Config.init_disclaimers()
        assert Config.disclaimers == ""


@pytest.mark.run(order=1)
def test_init_disclaimers_error():
    def mock_read_disclaimers():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_disclaimers', mock_read_disclaimers):
        Config._config = None
        Config.init_disclaimers()
        assert Config.disclaimers is None


@pytest.mark.run(order=1)
def test_init_municipalities():
    Config._config = None
    with patch.object(Config, '_read_municipalities', return_value=""):
        assert Config.municipalities is None
        Config.init_municipalities()
        assert Config.municipalities == ""


@pytest.mark.run(order=1)
def test_init_municipalities_error():
    def mock_read_municipalities():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_municipalities', mock_read_municipalities):
        Config._config = None
        Config.init_municipalities()
        assert Config.municipalities is None


@pytest.mark.run(order=1)
def test_init_document_types():
    Config._config = None
    with patch.object(Config, '_read_document_types', return_value=""):
        assert Config.document_types is None
        Config.init_document_types()
        assert Config.document_types == ""


@pytest.mark.run(order=1)
def test_init_document_types_error():
    def mock_read_document_types():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_document_types', mock_read_document_types):
        Config._config = None
        Config.init_document_types()
        assert Config.document_types is None


@pytest.mark.run(order=1)
def test_init_real_estate_types():
    Config._config = None
    with patch.object(Config, '_read_real_estate_types', return_value=""):
        assert Config.real_estate_types is None
        Config.init_real_estate_types()
        assert Config.real_estate_types == ""


@pytest.mark.run(order=1)
def test_init_real_estate_types_error():
    def mock_read_real_estate_types():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_real_estate_types', mock_read_real_estate_types):
        Config._config = None
        Config.init_real_estate_types()
        assert Config.real_estate_types is None


@pytest.mark.run(order=1)
def test_init_map_layering():
    Config._config = None
    with patch.object(Config, '_read_map_layering', return_value=""):
        assert Config.map_layering is None
        Config.init_map_layering()
        assert Config.map_layering == ""


@pytest.mark.run(order=1)
def test_init_map_layering_error():
    def mock_read_map_layering():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_map_layering', mock_read_map_layering):
        Config._config = None
        Config.init_map_layering()
        assert Config.map_layering is None


@pytest.mark.run(order=1)
def test_init_themes():
    Config._config = None
    with patch.object(Config, '_read_themes', return_value=""):
        assert Config.themes is None
        Config.init_themes()
        assert Config.themes == ""


@pytest.mark.run(order=1)
def test_init_themes_error():
    def mock_read_themes():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_themes', mock_read_themes):
        Config._config = None
        Config.init_themes()
        assert Config.themes is None


@pytest.mark.run(order=1)
def test_init_theme_document():
    Config._config = None
    with patch.object(Config, '_read_theme_document', return_value=""):
        assert Config.theme_document is None
        Config.init_theme_document()
        assert Config.theme_document == ""


@pytest.mark.run(order=1)
def test_init_theme_document_error():
    def mock_read_theme_document():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_theme_document', mock_read_theme_document):
        Config._config = None
        Config.init_theme_document()
        assert Config.theme_document is None


@pytest.mark.run(order=1)
def test_init_general_information():
    Config._config = None
    with patch.object(Config, '_read_general_information', return_value=""):
        assert Config.general_information is None
        Config.init_general_information()
        assert Config.general_information == ""


@pytest.mark.run(order=1)
def test_init_general_information_error():
    def mock_read_general_information():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_general_information', mock_read_general_information):
        Config._config = None
        Config.init_general_information()
        assert Config.general_information is None


@pytest.mark.run(order=1)
def test_init_law_status():
    Config._config = None
    with patch.object(Config, '_read_law_status', return_value=""):
        assert Config.law_status is None
        Config.init_law_status()
        assert Config.law_status == ""


@pytest.mark.run(order=1)
def test_init_law_status_error():
    def mock_read_law_status():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_law_status', mock_read_law_status):
        Config._config = None
        Config.init_law_status()
        assert Config.law_status is None


@pytest.mark.run(order=1)
def test_init_documents():
    Config._config = None
    with patch.object(Config, '_read_documents', return_value=""):
        assert Config.documents is None
        Config.init_documents()
        assert Config.documents == ""


@pytest.mark.run(order=1)
def test_init_documents_error():
    def mock_read_documents():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_documents', mock_read_documents):
        Config._config = None
        Config.init_documents()
        assert Config.documents is None


@pytest.mark.run(order=1)
def test_init_offices():
    Config._config = None
    with patch.object(Config, '_read_offices', return_value=""):
        assert Config.offices is None
        Config.init_offices()
        assert Config.offices == ""


@pytest.mark.run(order=1)
def test_init_offices_error():
    def mock_read_offices():
        raise ProgrammingError('a', 'b', 'c')
    with patch.object(Config, '_read_offices', mock_read_offices):
        Config._config = None
        Config.init_offices()
        assert Config.offices is None


@pytest.fixture()
def availabilities_records():
    yield [AvailabilityRecord(2771, 'ch.Nutzungsplanung', True),
           AvailabilityRecord(2772, 'ch.Nutzungsplanung', False)]


@pytest.mark.parametrize('test_value,expected_value', [
    ({"theme_code": "ch.Nutzungsplanung",
      "fosnr": 2771}, True),
    ({"theme_code": "ch.Nutzungsplanung",
      "fosnr": 2772}, False)
])
@pytest.mark.run(order=1)
def test_availability_by_theme_code_municipality_fosnr(test_value, expected_value, availabilities_records):
    Config.availabilities = availabilities_records
    assert Config.availability_by_theme_code_municipality_fosnr(
        test_value.get("theme_code"), test_value.get("fosnr")) == expected_value
    assert Config.availability_by_theme_code_municipality_fosnr('notInList', test_value.get("fosnr")) is True
    assert Config.availability_by_theme_code_municipality_fosnr(test_value.get("theme_code"), 0) is True


@pytest.mark.run(order=1)
def test_availability_by_theme_code_municipality_fosnr_config_none():
    Config.availabilities = None
    with pytest.raises(ConfigurationError):
        Config.availability_by_theme_code_municipality_fosnr('BN', 2771)


@pytest.fixture()
def law_status_lookups():
    yield [{"data_code": "inKraft",
            "transfer_code": "inKraft",
            "extract_code": "inForce"},
           {"data_code": "AenderungMitVorwirkung",
            "transfer_code": "AenderungMitVorwirkung",
            "extract_code": "changeWithPreEffect"}]


@pytest.mark.parametrize('test_value,expected_value', [
    ({"theme_code": "ch.Nutzungsplanung",
      "key": "data_code",
      "code": "inKraft"}, "inForce"),
    ({"theme_code": "ch.Nutzungsplanung",
      "key": "data_code",
      "code": "AenderungMitVorwirkung"}, "changeWithPreEffect")
])
@pytest.mark.run(order=1)
def test_get_law_status_lookup_by_theme_code_key_code(test_value, expected_value, law_status_lookups):
    with patch.object(Config, 'get_law_status_lookups', return_value=law_status_lookups):
        assert Config.get_law_status_lookup_by_theme_code_key_code(
            test_value.get("theme_code"),
            test_value.get("key"),
            test_value.get("code")).get("extract_code") == expected_value


@pytest.mark.parametrize('test_value', [
    ({}),
    ([]),
    (None)
])
@pytest.mark.run(order=1)
def test_get_law_status_lookup_by_theme_code_key_code_no_key(test_value):
    with patch.object(Config, 'get_law_status_lookups', return_value=test_value):
        with pytest.raises(ConfigurationError):
            Config.get_law_status_lookup_by_theme_code_key_code(
                "ch.Nutzungsplanung",
                "data_code",
                "inKraft")


@pytest.mark.run(order=1)
def test_get_config():
    Config._config = None
    assert Config.get_config() is None
    Config._config = {}
    assert Config.get_config() == {}
    # set config back to None.
    Config._config = None


@pytest.mark.parametrize('test_value,expected_value', [
    ({'real_estate': {'plan_for_land_register_main_page': {}}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_plan_for_land_register_main_page_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_plan_for_land_register_main_page_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_plan_for_land_register_main_page_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_plan_for_land_register_main_page_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'real_estate': {'plan_for_land_register': {}}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_plan_for_land_register_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_plan_for_land_register_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_plan_for_land_register_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_plan_for_land_register_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'address': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_address_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_address_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_address_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_address_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'theme_document': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_theme_document_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_theme_document_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_theme_document_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_theme_document_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'document_types': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_document_types_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_document_types_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_document_types_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_document_types_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'disclaimer': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_disclaimer_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_disclaimer_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_disclaimer_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_disclaimer_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'general_information': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_info_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_info_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_info_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_info_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'documents': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_document_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_document_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_document_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_document_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'offices': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_office_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_office_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_office_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_office_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'municipality': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_municipality_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_municipality_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_municipality_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_municipality_config()


@pytest.mark.parametrize('test_value,expected_value', [
    ({'availability': {}}, {}),
    ({'not_expecting_key': {}}, None)
])
@pytest.mark.run(order=-1)
def test_get_availability_config(test_value, expected_value):
    Config._config = test_value
    assert Config.get_availability_config() == expected_value


@pytest.mark.run(order=-1)
def test_get_availability_config_none():
    Config._config = None
    with pytest.raises(AssertionError):
        Config.get_availability_config()


@pytest.fixture()
def municipality_records():
    yield [MunicipalityRecord(2771, 'Gemeinde', True),
           MunicipalityRecord(2772, 'Gemeinde2', False)]


@pytest.mark.parametrize('test_value,expected_index', [
    (2771, 0),
    (2772, 1)
])
@pytest.mark.run(order=1)
def test_municipality_by_fosnr(test_value, expected_index, municipality_records):
    Config.municipalities = municipality_records
    assert Config.municipality_by_fosnr(test_value) == municipality_records[expected_index]


@pytest.mark.run(order=1)
def test_municipality_by_fosnr_config_none():
    Config.municipalities = None
    with pytest.raises(ConfigurationError):
        Config.municipality_by_fosnr(0)


@pytest.mark.run(order=1)
def test_municipality_by_fosnr_not_in_list(municipality_records):
    Config.municipalities = municipality_records
    with pytest.raises(ConfigurationError):
        Config.municipality_by_fosnr(0)


@pytest.mark.parametrize('test_value,expected_value', [
    ({"law_status_lookup": {}}, {}),
    ({"law_status_lookup": ""}, "")
])
@pytest.mark.run(order=1)
def test_get_law_status_lookups(test_value, expected_value):
    Config._config = None
    with patch.object(Config, 'get_theme_config_by_code', return_value=test_value):
        assert Config.get_law_status_lookups('theme_code') == expected_value


@pytest.mark.run(order=1)
def test_get_law_status_lookups_lookups_none():
    Config._config = None
    with patch.object(Config, 'get_theme_config_by_code', return_value={"law_status_lookup": None}):
        with pytest.raises(ConfigurationError):
            Config.get_law_status_lookups('theme_code')


@pytest.mark.parametrize('test_value', [
    ({"data_code": "inKraft",
      "transfer_code": "inKraft",
      "extract_code": "inForce"}),
    ({"data_code": "AenderungMitVorwirkung",
      "transfer_code": "AenderungMitVorwirkung",
      "extract_code": "changeWithPreEffect"})
])
@pytest.mark.run(order=1)
def test_get_law_status_lookup_by_data_code(test_value):
    with patch.object(Config, 'get_law_status_lookup_by_theme_code_key_code', return_value=test_value):
        assert Config.get_law_status_lookup_by_data_code(
            "theme_code",
            "data_code") == test_value
