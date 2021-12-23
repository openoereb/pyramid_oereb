import pytest
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, DateTime, Column
from pyramid_oereb.contrib.data_sources.standard import create_schema_sql, tables, create_tables_sql, create_sql


@pytest.fixture
def simple_table_base():
    base = declarative_base()
    schema_name = 'test'
    class Test(base):
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'test_table'
        test_column = Column(String, primary_key=True)
    yield base, Test, schema_name


@pytest.fixture
def datetime_table_base():
    base = declarative_base()
    schema_name = 'test'
    class Test(base):
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'test_table'
        test_column = Column(DateTime, primary_key=True)
    yield base, Test, schema_name


def test_create_schema_sql():
    sql = create_schema_sql('test')
    assert sql == 'CREATE SCHEMA IF NOT EXISTS test;'


def test_create_tables_sql(simple_table_base):
    sql = create_tables_sql(tables(simple_table_base[0]))
    expected_sql = 'CREATE TABLE test.test_table (test_column VARCHAR NOT NULL, PRIMARY KEY (test_column));'
    assert sql.replace('\n', '').replace('\t','') == expected_sql


def test_create_tables_sql_date(datetime_table_base):
    sql = create_tables_sql(tables(datetime_table_base[0]))
    expected_sql = 'CREATE TABLE test.test_table (test_column TIMESTAMP WITHOUT TIME ZONE NOT NULL, PRIMARY KEY (test_column));'
    assert sql.replace('\n', '').replace('\t','') == expected_sql


def test_create_sql(simple_table_base):
    sql = create_sql(simple_table_base[2], tables(simple_table_base[0]))
    expected_sql = 'CREATE SCHEMA IF NOT EXISTS test;CREATE TABLE test.test_table (test_column VARCHAR NOT NULL, PRIMARY KEY (test_column));'
    assert sql.replace('\n', '').replace('\t', '') == expected_sql
