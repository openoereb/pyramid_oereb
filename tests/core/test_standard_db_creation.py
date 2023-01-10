# -*- coding: utf-8 -*-
import pytest
from io import StringIO
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError


@pytest.mark.run(order=-9)
def test_create_standard_db(config_path, dbsession, transact):
    from pyramid_oereb.contrib.data_sources.create_tables import create_tables_from_standard_configuration
    sql_file = StringIO()
    standart_table_source = 'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource'
    create_tables_from_standard_configuration(config_path, standart_table_source, sql_file=sql_file)

    # tables already exist in DB => error
    with pytest.raises(ProgrammingError):
        sql_file.seek(0)
        dbsession.execute(text(sql_file.read()))


@pytest.mark.run(order=-9)
def test_create_main_schema(config_path, dbsession, transact):
    from pyramid_oereb.contrib.data_sources.create_tables import create_main_schema_from_configuration_
    sql_file = StringIO()
    create_main_schema_from_configuration_(config_path, sql_file=sql_file)

    # tables already exist in DB => error
    with pytest.raises(ProgrammingError):
        sql_file.seek(0)
        dbsession.execute(text(sql_file.read()))


@pytest.mark.run(order=-9)
def test_create_standard_db_if_not_exists(config_path, dbsession, transact):
    from pyramid_oereb.contrib.data_sources.create_tables import create_tables_from_standard_configuration
    sql_file = StringIO()
    standart_table_source = 'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource'
    create_tables_from_standard_configuration(
        config_path,
        standart_table_source,
        sql_file=sql_file,
        if_not_exists=True
    )

    sql_file.seek(0)
    dbsession.execute(text(sql_file.read()))


@pytest.mark.run(order=-9)
def test_create_main_schema_if_not_exists(config_path, dbsession, transact):
    from pyramid_oereb.contrib.data_sources.create_tables import create_main_schema_from_configuration_
    sql_file = StringIO()
    create_main_schema_from_configuration_(config_path, sql_file=sql_file, if_not_exists=True)

    sql_file.seek(0)
    dbsession.execute(text(sql_file.read()))
