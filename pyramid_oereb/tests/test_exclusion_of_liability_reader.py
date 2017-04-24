# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.exclusion_of_liability import ExclusionOfLiabilityReader
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    reader = ExclusionOfLiabilityReader(
        config_reader.get_exclusion_of_liability_config().get('source').get('class'),
        **config_reader.get_exclusion_of_liability_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'id': 1, 'title': 'Disclaimer', 'content': 'No warranty!'}
])
def test_read(param):
    reader = ExclusionOfLiability(
        config_reader.get_exclusion_of_liability_config().get('source').get('class'),
        **config_reader.get_exclusion_of_liability_config().get('source').get('params')
    )
    with pytest.raises(NoResultFound):
        reader.read(param.get('id'), param.get('title'), param.get('content'))

# TODO: Implement tests for return values, not possible now, cause there is no data in database
