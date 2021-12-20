# -*- coding: utf-8 -*-

import re
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql


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


def create_tables_sql(tables_to_create, if_not_exists=False):
    """
    Args:
        tables_to_create (list of sqlalchemy.schema.Table): The table objects from sqlalchemy.
    Returns:
        a string with the sql statement used to create the tables
    """
    sqls = []
    for table in tables_to_create:
        sqls.append(
            '{};\n'.format(
                str(CreateTable(table, if_not_exists=if_not_exists)
                    .compile(dialect=postgresql.dialect())).replace('DATETIME', 'timestamp')
            )
        )
    return ''.join(sqls)


def create_sql(schema_name, tables_to_create, if_not_exists=False):
    sqls = [
        create_schema_sql(schema_name),
        create_tables_sql(tables_to_create, if_not_exists)
    ]
    return '\n'.join(sqls)
