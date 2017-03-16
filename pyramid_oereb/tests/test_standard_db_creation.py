# -*- coding: utf-8 -*-
import os
import pytest

from pyramid.config import ConfigurationError

__author__ = 'Clemens Rudert'
__create_date__ = '16.03.17'


@pytest.mark.run(order=1)
def test_create_standard_db():
    from pyramid_oereb.standard import create_tables
    db_url = os.environ.get('SQLALCHEMY_URL')
    if db_url:
        create_tables(connection_string=db_url)
    else:
        raise ConfigurationError()
