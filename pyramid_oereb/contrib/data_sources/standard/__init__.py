# -*- coding: utf-8 -*-

import re

from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable


def convert_camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def convert_camel_case_to_text_form(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)


def tables(base):
    return base.metadata.sorted_tables


def create_schema_sql(schema_name):
    return 'CREATE SCHEMA IF NOT EXISTS {0};'.format(schema_name)


def create_tables_sql(db_connection, tables):
    """
    Args:
        db_connection (str): The db connection string.
        tables (list of sqlalchemy.schema.Table): The table objects from sqlalchemy.
    Returns:
        a string with the sql statement used to create the tables
    """
    sqls = []
    engine = create_engine(db_connection, echo=True)
    for table in tables:
        sqls.append(
            '{};\n'.format(
                str(CreateTable(table).compile(engine)).replace('DATETIME', 'timestamp')
            )
        )
    return ''.join(sqls)


def create_sql(schema_name, db_connection, tables):
    sqls = [
        create_schema_sql(schema_name),
        create_tables_sql(db_connection, tables)
    ]
    return '\n'.join(sqls)


def drop_sql(schema_name):
    return 'DROP SCHEMA IF EXISTS {0} CASCADE;'.format(schema_name)


def execute_sql(db_connection, sql):
    connection = create_engine(db_connection, echo=True).connect()
    try:
        connection.execute(sql)
    finally:
        connection.close()
