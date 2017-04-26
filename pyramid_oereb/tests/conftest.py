# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine

from pyramid_oereb.lib.config import parse, ConfigReader
from pyramid_oereb.models import PyramidOerebMainMunicipality, PyramidOerebMainGlossary

db_url = parse('pyramid_oereb_test.yml', 'pyramid_oereb').get('db_connection')
config_reader = ConfigReader('pyramid_oereb_test.yml', 'pyramid_oereb')


@pytest.fixture()
def connection():
    engine = create_engine(db_url)
    connection = engine.connect()

    # Add dummy municipality
    connection.execute('TRUNCATE {schema}.{table};'.format(
        schema=PyramidOerebMainMunicipality.__table__.schema,
        table=PyramidOerebMainMunicipality.__table__.name
    ))
    connection.execute(PyramidOerebMainMunicipality.__table__.insert(), {
        'fosnr': 1234,
        'name': 'Test',
        'published': True,
        'geom': 'SRID=2056;MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)))'
    })

    # Add dummy glossary
    connection.execute('TRUNCATE {schema}.{table};'.format(
        schema=PyramidOerebMainGlossary.__table__.schema,
        table=PyramidOerebMainGlossary.__table__.name
    ))
    connection.execute(PyramidOerebMainGlossary.__table__.insert(), {
        'id': 1,
        'title': u'SGRF',
        'content': u'Service de la géomatique et du registre foncier'
    })

    connection.close()
    return connection
