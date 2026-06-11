from unittest.mock import MagicMock, patch

import pytest

from pyramid_oereb.contrib.stats.scripts.create_stats_tables import _create_views


def test_create_views_sanitization():
    with (patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.configparser.ConfigParser')
            as mock_config_parser,
            patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.SQLAlchemyHandler'),
            patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.Template') as mock_template):
        malicious_schema = "stats_schema; DROP SCHEMA main_schema;"
        malicious_table = "main_table; DROP TABLE secrets;--"

        mock_config = MagicMock()
        mock_config.__getitem__.return_value = {
            'args': "[{'tableargs': {'schema': " + repr(malicious_schema) + "}, 'tablename': " + repr(
                malicious_table) + "}]"
        }
        mock_config_parser.return_value = mock_config

        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "DROP VIEW IF EXISTS dummy;"
        mock_template.return_value = mock_template_instance

        _create_views('mock_config.ini')

        _, kwargs = mock_template_instance.render.call_args
        assert kwargs['schema_name'] == "stats_schemaDROPSCHEMAmain_schema"
        assert kwargs['tablename'] == "main_tableDROPTABLEsecrets"


def test_invalid_schema_name_raises_error():
    with (patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.configparser.ConfigParser')
            as mock_config_parser,
            patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.SQLAlchemyHandler'),
            patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.Template') as mock_template):
        mock_config = MagicMock()
        mock_config.__getitem__.return_value = {
            'args': "[{'tableargs': {'schema': '!!;'}, 'tablename': 'main_table'}]"
        }
        mock_config_parser.return_value = mock_config

        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "DROP VIEW IF EXISTS dummy;"
        mock_template.return_value = mock_template_instance

        with pytest.raises(ValueError) as ex_info:
            _create_views('mock_config.ini')

        assert ex_info.value.args[0] == "Invalid schema name after sanitization: '!!;' -> ''"


def test_invalid_table_name_raises_error():
    with (patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.configparser.ConfigParser')
            as mock_config_parser,
            patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.SQLAlchemyHandler'),
            patch('pyramid_oereb.contrib.stats.scripts.create_stats_tables.Template') as mock_template):
        mock_config = MagicMock()
        mock_config.__getitem__.return_value = {
            'args': "[{'tableargs': {'schema': 'stats_schema'}, 'tablename': '!!;'}]"
        }
        mock_config_parser.return_value = mock_config

        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "DROP VIEW IF EXISTS dummy;"
        mock_template.return_value = mock_template_instance

        with pytest.raises(ValueError) as ex_info:
            _create_views('mock_config.ini')

        assert ex_info.value.args[0] == "Invalid table name after sanitization: '!!;' -> ''"
