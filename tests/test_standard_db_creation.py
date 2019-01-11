# -*- coding: utf-8 -*-
import pytest

from tests import pyramid_oereb_test_yml


@pytest.mark.run(order=-2)
def test_create_standard_db():
    assert pyramid_oereb_test_yml is not None
    from pyramid_oereb.standard import create_tables_from_standard_configuration
    create_tables_from_standard_configuration(pyramid_oereb_test_yml)


@pytest.mark.run(order=-3)
def test_drop_tables():
    assert pyramid_oereb_test_yml is not None
    from pyramid_oereb.standard import drop_tables_from_standard_configuration
    drop_tables_from_standard_configuration(pyramid_oereb_test_yml)
