# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine

from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.glossary import GlossaryReader
from pyramid_oereb.models import PyramidOerebMainGlossary
from pyramid_oereb.tests.conftest import config_reader, db_url


@pytest.fixture()
def connection():
    engine = create_engine(db_url)
    connection = engine.connect()
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


@pytest.mark.run(order=2)
def test_init():
    reader = GlossaryReader(
        config_reader.get_glossary_config().get('source').get('class'),
        **config_reader.get_glossary_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [{
    'id': 1,
    'title': u'SGRF',
    'content': u'Service de la géomatique et du registre foncier'
}])
def test_read(param):
    reader = GlossaryReader(
        config_reader.get_glossary_config().get('source').get('class'),
        **config_reader.get_glossary_config().get('source').get('params')
    )
    results = reader.read(param.get('id'), param.get('title'), param.get('content'))
    assert isinstance(results, list)
    assert len(results) == 0

# TODO: Implement tests for return values, not possible now, cause there is no data in database
