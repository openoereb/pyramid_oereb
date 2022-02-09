import os

import pytest
import time
import json
from unittest.mock import patch
from pyramid.paster import get_app, setup_logging
from webtest import TestApp
from pyramid_oereb.core.config import Config
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from pyramid_oereb.contrib.stats.scripts.create_stats_tables import _create_views


@pytest.fixture(scope="session")
def webtestapp():
    Config._config = None
    setup_logging('tests/resources/test.ini#main', global_conf=os.environ)
    app = get_app('tests/resources/test.ini#main', options=os.environ)
    test_app = TestApp(app)
    return test_app


def test_log_logo(webtestapp):
    """
    Test webapp entrypoint with insufficiently initialized test data
    """
    with pytest.raises(Exception):
        webtestapp.get("/oereb/image/logo/oereb/de.png")


def test_log_app(webtestapp, logo_test_data, clear_stats_db_engine, stats_db_url):
    with patch.object(Config, 'logos', logo_test_data):
        webtestapp.get("/oereb/image/logo/oereb/de.png")

    # wait maximum 15s for async log handler to complete its oprations (db creation and log message)
    eng = create_engine(stats_db_url)
    for i in range(30):
        try:
            log_result = eng.execute(
                "select logger, level, msg from oereb_logs.logs order by created_at desc"
            ).first()
            if log_result is not None:
                break
        except OperationalError:
            pass  # if DB does not exist yet, it shall not be cleared
        time.sleep(.5)
        print(f"Waiting for async logs - {i}")
    assert i < 29, "Timeout reached while waiting for log results"
    assert log_result[0] == 'JSON'
    assert log_result[1] == 'INFO'
    assert json.loads(log_result[2]) == {
        "response": {
            "status_code": 200,
            "headers": {
                "Content-Length": "18095",
                "Content-Type": "image/png"
            },
            "extras": None
        },
        "request": {
            "headers": {"Host": "localhost:80"},
            "traversed": "()",
            "parameters": {},
            "path": "/oereb/image/logo/oereb/de.png",
            "view_name": ""
        }
    }


def test_create_stats_tables():
    _create_views('tests/resources/test.ini')
