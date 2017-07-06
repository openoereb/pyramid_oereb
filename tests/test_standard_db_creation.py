# -*- coding: utf-8 -*-
import pytest

from tests.conftest import pyramid_oereb_test_yml


@pytest.mark.run(order=-1)
def test_create_standard_db():
    assert pyramid_oereb_test_yml is not None
    from pyramid_oereb.standard import _create_tables_from_standard_configuration_
    _create_tables_from_standard_configuration_(
        configuration_yaml_path=pyramid_oereb_test_yml
    )


@pytest.mark.run(order=-2)
def test_drop_tables():
    assert pyramid_oereb_test_yml is not None
    from pyramid_oereb.standard import _drop_tables_from_standard_configuration_
    _drop_tables_from_standard_configuration_(
        configuration_yaml_path=pyramid_oereb_test_yml
    )
