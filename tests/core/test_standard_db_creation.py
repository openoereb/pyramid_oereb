# -*- coding: utf-8 -*-
import pytest


@pytest.mark.run(order=-9)
def test_create_standard_db(config_path):
    from pyramid_oereb.contrib.data_sources.create_tables import create_tables_from_standard_configuration
    create_tables_from_standard_configuration(config_path)
