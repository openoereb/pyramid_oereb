# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid.config import ConfigurationError

from pyramid_oereb.lib.adapter import FileAdapter
from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.office import OfficeRecord


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
def test_wrong_configuration_section():
    Config._config = None
    with pytest.raises(ConfigurationError):
        Config.init('./tests/resources/test_config.yml', 'invalidsection')


@pytest.mark.run(order=-1)
def test_configuration_file_not_found():
    Config._config = None
    with pytest.raises(IOError) as excinfo:
        Config.init('not_existing_config.yml', 'invalidsection')
    assert ', Current working directory is ' in str(excinfo.value)


@pytest.mark.run(order=-1)
def test_parse_configuration():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'section2')
    assert Config.get('param1') == 1
    assert len(Config.get('param2')) == 2
    assert Config.get('param2')[0] == 'first'
    assert Config.get('param2')[1] == 'second'


@pytest.mark.run(order=-1)
def test_get_plr_cadastre_authority():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    plr_cadastre_authority = Config.get_plr_cadastre_authority()
    assert isinstance(plr_cadastre_authority, OfficeRecord)


@pytest.mark.run(order=-1)
def test_get_logo_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    logos = Config.get_logo_config()
    assert isinstance(logos, dict)
    logo_oereb = logos.get('oereb')
    assert isinstance(logo_oereb, ImageRecord)
    assert logo_oereb.content == FileAdapter().read(Config.get('logo').get('oereb'))


@pytest.mark.run(order=-1)
@pytest.mark.parametrize('language', [
    None,
    'de',
    'fr',
    'it'
])
def test_get_logo_multilingual(language):
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    Config.get('logo')['oereb'] = {
        'de': 'pyramid_oereb/standard/logo_oereb_de.png',
        'fr': 'pyramid_oereb/standard/logo_oereb_fr.png',
        'it': 'pyramid_oereb/standard/logo_oereb_it.png'
    }
    logos = Config.get_logo_config(language=language)
    assert isinstance(logos, dict)
    logo_oereb = logos.get('oereb')
    if language is None:
        assert logo_oereb.content == FileAdapter().read(Config.get('logo').get('oereb').get('de'))
    else:
        assert logo_oereb.content == FileAdapter().read(Config.get('logo').get('oereb').get(language))


@pytest.mark.run(order=-1)
def test_get_all_federal():
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    all_federal = Config.get_all_federal()
    assert isinstance(all_federal, list)
    assert len(all_federal) == 10
    assert 'RailwaysProjectPlanningZones' in all_federal


@pytest.mark.run(order=-1)
def test_get_base_data():
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    date = datetime.datetime(2017, 2, 1)
    base_data = Config.get_base_data(date)
    assert isinstance(base_data, dict)
    assert base_data.get('de') == 'Daten der amtlichen Vermessung. Stand der amtlichen ' \
                                  'Vermessung: 01.02.2017.'


@pytest.mark.run(order=-1)
def test_get_oereblex_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
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
def test_get_layer_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    layer_index, layer_opacity = Config.get_layer_config('LandUsePlans')
    assert layer_index == 1
    assert layer_opacity == 0.25
    layer_index, layer_opacity = Config.get_layer_config('MotorwaysProjectPlaningZones')
    assert layer_index is None
    assert layer_opacity is None


@pytest.mark.run(order=-1)
def test_get_real_estate_main_page_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    lang = Config.get('default_language')
    plan_for_land_register_main_page_config = Config.get_plan_for_land_register_main_page_config()
    assert plan_for_land_register_main_page_config.get('reference_wms')[lang] == \
        'https://wms.ch/?BBOX=2475000,1065000,2850000,1300000'
    assert plan_for_land_register_main_page_config.get('layer_index') == 2
    assert plan_for_land_register_main_page_config.get('layer_opacity') == 0.5


@pytest.mark.run(order=-1)
def test_get_real_estate_type_by_mapping():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')

    mapping = Config.get_real_estate_type_by_mapping('Liegenschaft')
    assert mapping == 'RealEstate'

    mapping = Config.get_real_estate_type_by_mapping('Baurecht')
    assert mapping == 'Distinct_and_permanent_rights.BuildingRight'

    mapping = Config.get_real_estate_type_by_mapping('Quellenrecht')
    assert mapping == 'Distinct_and_permanent_rights.right_to_spring_water'

    mapping = Config.get_real_estate_type_by_mapping('Konzessionsrecht')
    assert mapping == 'Distinct_and_permanent_rights.concession'

    mapping = Config.get_real_estate_type_by_mapping('weitere')
    assert mapping == 'Distinct_and_permanent_rights.other'

    mapping = Config.get_real_estate_type_by_mapping('Bergwerk')
    assert mapping == 'Mineral_rights'
