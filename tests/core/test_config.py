# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.exc import ProgrammingError

from unittest.mock import patch

from pyramid.config import ConfigurationError
from unittest.mock import patch

# from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.office import OfficeRecord


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
def test_get_document_config_none():
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
