# -*- coding: utf-8 -*-
import pytest
from io import StringIO
from sqlalchemy.exc import ProgrammingError


@pytest.mark.run(order=-9)
def test_create_standard_db(config_path, dbsession, transact):
    from pyramid_oereb.contrib.data_sources.create_tables import create_tables_from_standard_configuration
    sql_file = StringIO()
    create_tables_from_standard_configuration(config_path, sql_file=sql_file)

    # tables already exist in DB => error
    with pytest.raises(ProgrammingError):
        sql_file.seek(0)
        dbsession.execute(sql_file.read())


@pytest.mark.run(order=-9)
def test_create_standard_db_if_not_exists(config_path, dbsession, transact):
    from pyramid_oereb.contrib.data_sources.create_tables import create_tables_from_standard_configuration
    sql_file = StringIO()
    create_tables_from_standard_configuration(config_path, sql_file=sql_file, if_not_exists=True)

    sql_file.seek(0)
    dbsession.execute(sql_file.read())
