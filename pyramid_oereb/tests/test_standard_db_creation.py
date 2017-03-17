# -*- coding: utf-8 -*-
import pytest

from pyramid.config import ConfigurationError

__author__ = 'Clemens Rudert'
__create_date__ = '16.03.17'


@pytest.mark.run(order=1)
def test_create_standard_db():
    from pyramid_oereb.standard import create_tables
    create_tables(configuration_yaml_path='pyramid_oereb_test.yml')
