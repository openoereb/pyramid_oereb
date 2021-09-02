# -*- coding: utf-8 -*-
import pytest

from tests import pyramid_oereb_test_yml


@pytest.mark.run(order=-9)
def test_create_standard_db():
    assert pyramid_oereb_test_yml is not None
    from pyramid_oereb.standard.create_tables import create_tables_from_standard_configuration
    create_tables_from_standard_configuration(pyramid_oereb_test_yml)


@pytest.mark.run(order=-10)
def test_drop_tables():
    assert pyramid_oereb_test_yml is not None
    from pyramid_oereb.standard.drop_tables import drop_tables_from_standard_configuration
    drop_tables_from_standard_configuration(pyramid_oereb_test_yml)
