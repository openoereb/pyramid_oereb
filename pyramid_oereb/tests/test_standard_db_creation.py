# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.tests.conftest import pyramid_oereb_test_yml


@pytest.mark.run(order=1)
def test_create_standard_db():
    from pyramid_oereb.standard import _create_tables_from_standard_configuration_
    _create_tables_from_standard_configuration_(
        configuration_yaml_path=pyramid_oereb_test_yml
    )


@pytest.mark.run(order=0)
def test_drop_tables():
    from pyramid_oereb.standard import _create_tables_from_standard_configuration_, \
        _drop_tables_from_standard_configuration_
    _create_tables_from_standard_configuration_(
        configuration_yaml_path=pyramid_oereb_test_yml
    )
    _drop_tables_from_standard_configuration_(
        configuration_yaml_path=pyramid_oereb_test_yml
    )
