# -*- coding: utf-8 -*-
import logging
from sqlalchemy.orm import Session
from pyramid_oereb.core.adapter import DatabaseAdapter


def test_init():
    adapter = DatabaseAdapter()
    assert isinstance(adapter._connections_, dict)


def test_get_connections_instance():
    adapter = DatabaseAdapter()
    assert isinstance(adapter.get_connections(), dict)


def test_add_connection():
    db_url = 'postgresql://adapter_user:adapter_pswd@adapter-tests-00:5432/adapter-db'
    adapter = DatabaseAdapter()
    adapter.add_connection(db_url)
    assert isinstance(adapter.get_session(db_url), Session)


def test_add_connection_already_exists(caplog):
    caplog.set_level(logging.INFO)
    db_url = 'postgresql://adapter_user:adapter_pswd@adapter-tests-01:5432/adapter-db'
    adapter = DatabaseAdapter()
    adapter.add_connection(db_url)
    assert 'Connection already exists: {0}'.format(db_url) not in caplog.text
    adapter.add_connection(db_url)
    assert 'Connection already exists: {0}'.format(db_url) in caplog.text


def test_get_connections():
    db_url = 'postgresql://adapter_user:adapter_pswd@adapter-tests-02:5432/adapter-db'
    test_connection = {db_url: {"engine": "test_engine", "session": "test_session"}}
    adapter = DatabaseAdapter()
    adapter._connections_ = test_connection
    assert adapter.get_connections() == test_connection


def test_get_session_that_exists():
    db_url = 'postgresql://adapter_user:adapter_pswd@adapter-tests-03:5432/adapter-db'
    adapter = DatabaseAdapter()
    adapter.add_connection(db_url)
    n_connections = len(adapter.get_connections())
    assert adapter.get_connections().get(db_url) is not None
    session_00 = adapter.get_session(db_url)
    assert isinstance(session_00, Session)
    assert len(adapter.get_connections()) == n_connections


def test_get_session_that_does_not_exists():
    db_url = 'postgresql://adapter_user:adapter_pswd@adapter-tests-04:5432/adapter-db'
    adapter = DatabaseAdapter()
    n_connections = len(adapter.get_connections())
    assert adapter.get_connections().get(db_url, None) is None
    session_00 = adapter.get_session(db_url)
    assert adapter.get_connections().get(db_url, None) is not None
    assert isinstance(session_00, Session)
    assert len(adapter.get_connections()) == (n_connections + 1)
