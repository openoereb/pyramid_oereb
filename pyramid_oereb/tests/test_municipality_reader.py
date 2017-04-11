# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine

from pyramid_oereb.lib.records.municipality import MunicipalityRecord
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.municipality import MunicipalityReader
from pyramid_oereb.models import PyramidOerebMainMunicipality
from pyramid_oereb.tests.conftest import config_reader, db_url


@pytest.fixture()
def connection():
    engine = create_engine(db_url)
    connection = engine.connect()
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
    connection.close()
    return connection


@pytest.mark.run(order=2)
def test_init():
    reader = MunicipalityReader(
        config_reader.get_municipality_config().get('source').get('class'),
        **config_reader.get_municipality_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(connection):
    assert connection.closed
    reader = MunicipalityReader(
        config_reader.get_municipality_config().get('source').get('class'),
        **config_reader.get_municipality_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, MunicipalityRecord)
    assert result.fosnr == 1234
    assert result.name == 'Test'
    assert result.published
    assert result.geom == 'MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)))'
# TODO: Implement tests for return values, not possible now, cause there is no data in database
