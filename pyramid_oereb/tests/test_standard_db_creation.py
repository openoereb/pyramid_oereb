# -*- coding: utf-8 -*-
import pytest

__author__ = 'Clemens Rudert'
__create_date__ = '16.03.17'


@pytest.mark.run(order=1)
def test_create_standard_db():
    from pyramid_oereb.standard import _create_tables_
    _create_tables_(configuration_yaml_path='pyramid_oereb_test.yml')


@pytest.mark.run(order=0)
def test_drop_tables():
    from pyramid_oereb.standard import _create_tables_, _drop_tables_
    _create_tables_(configuration_yaml_path='pyramid_oereb_test.yml')
    _drop_tables_(configuration_yaml_path='pyramid_oereb_test.yml')
