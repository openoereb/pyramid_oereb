# -*- coding: utf-8 -*-
import os
import pytest
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session

from pyramid_oereb.lib.adapter import DatabaseAdapter

__author__ = 'Clemens Rudert'
__create_date__ = '16.03.17'


def test_init():
    adapter = DatabaseAdapter()
    assert isinstance(adapter._connections_, dict)


def test_get_connections():
    adapter = DatabaseAdapter()
    assert isinstance(adapter.get_connections(), dict)


def test_add_connection():
    test_connection_string = os.environ.get('SQLALCHEMY_URL')
    adapter = DatabaseAdapter()
    adapter.add_connection(test_connection_string)
    assert isinstance(adapter.get_session(test_connection_string), Session)


def test_add_existing_connection():
    test_connection_string = os.environ.get('SQLALCHEMY_URL')
    adapter = DatabaseAdapter()
    adapter.add_connection(test_connection_string)
    expected_length = len(adapter.get_connections())
    adapter.add_connection(test_connection_string)
    assert len(adapter.get_connections()) == expected_length


def test_add_connection_fail():
    adapter = DatabaseAdapter()
    with pytest.raises(ArgumentError):
        adapter.add_connection('not_a_connection_string')


def test_get_missing_connection():
    adapter = DatabaseAdapter()
    with pytest.raises(KeyError):
        adapter.get_session('connection_that_does_not_exist')
