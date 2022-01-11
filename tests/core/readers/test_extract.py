# -*- coding: utf-8 -*-
import pytest
from pyramid.path import DottedNameResolver
from shapely.geometry import MultiPolygon, Polygon

from pyramid_oereb.core.records.extract import ExtractRecord
from pyramid_oereb.core.records.plr import PlrRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord
from pyramid_oereb.core.records.municipality import MunicipalityRecord
from tests.mockrequest import MockParameter


@pytest.fixture
@pytest.mark.usefixtures('pyramid_oereb_test_config')
def plr_cadastre_authority(pyramid_oereb_test_config):
    yield pyramid_oereb_test_config.get_plr_cadastre_authority()


@pytest.fixture
@pytest.mark.usefixtures('pyramid_oereb_test_config')
def plr_sources(pyramid_oereb_test_config):
    plr_sources = []
    for plr in pyramid_oereb_test_config.get('plrs'):
        plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
        plr_sources.append(plr_source_class(**plr))
    yield plr_sources


@pytest.fixture
def real_estate():
    yield RealEstateRecord(
        u'test', u'BL', u'Laufen', 2770, 1000,
        MultiPolygon([Polygon([(0, 0), (4, 4), (4, 0)])]),
        ViewServiceRecord(
            {'de': 'test_link'},
            1, 1.0, 'de', 2056, None, None,
        )
    )


@pytest.fixture
def municipality():
    yield MunicipalityRecord(
        2771,
        u'FantasyMunicipality',
        True,
        geom=MultiPolygon()
    )


@pytest.mark.run(order=2)
def test_init(plr_sources, plr_cadastre_authority):
    from pyramid_oereb.core.readers.extract import ExtractReader

    reader = ExtractReader(plr_sources, plr_cadastre_authority)
    assert isinstance(reader._plr_sources_, list)


@pytest.mark.run(order=2)
def test_read(main_schema, land_use_plans, contaminated_sites, plr_sources, plr_cadastre_authority,
              real_estate, municipality):
    from pyramid_oereb.core.readers.extract import ExtractReader

    del main_schema, land_use_plans, contaminated_sites

    reader = ExtractReader(plr_sources, plr_cadastre_authority)
    extract = reader.read(MockParameter(), real_estate, municipality)
    assert isinstance(extract, ExtractRecord)
    plrs = extract.real_estate.public_law_restrictions
    assert isinstance(plrs, list)
    assert isinstance(plrs[0], PlrRecord)
    assert plrs[3].theme.code == 'ch.BelasteteStandorte'
    assert plrs[3].law_status.code == 'inForce'
