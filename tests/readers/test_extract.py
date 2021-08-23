# -*- coding: utf-8 -*-
import pytest
from pyramid.path import DottedNameResolver
from shapely.geometry import MultiPolygon, Polygon

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.lib.records.municipality import MunicipalityRecord
from pyramid_oereb.lib.readers.extract import ExtractReader
from tests.mockrequest import MockParameter


plr_cadastre_authority = Config.get_plr_cadastre_authority()

plr_sources = []
for plr in Config.get('plrs'):
    plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
    plr_sources.append(plr_source_class(**plr))

real_estate = RealEstateRecord(u'test', u'BL', u'Laufen', 2770, 1000,
                               MultiPolygon([Polygon([(0, 0), (4, 4), (4, 0)])]),
                               ViewServiceRecord(
                                   {'de': 'test_link'},
                                   1,
                                   1.0,
                               ))

municipality = MunicipalityRecord(
        2771,
        u'FantasyMunicipality',
        True,
        geom=MultiPolygon()
    )


@pytest.mark.run(order=2)
def test_init():
    reader = ExtractReader(plr_sources, plr_cadastre_authority)
    assert isinstance(reader._plr_sources_, list)


@pytest.mark.run(order=2)
def test_read():
    reader = ExtractReader(plr_sources, plr_cadastre_authority)
    extract = reader.read(MockParameter(), real_estate, municipality)
    assert isinstance(extract, ExtractRecord)
    plrs = extract.real_estate.public_law_restrictions
    assert isinstance(plrs, list)
    assert isinstance(plrs[0], PlrRecord)
    assert plrs[4].theme.code == 'MotorwaysBuildingLines'
    assert plrs[4].law_status.code == 'AenderungMitVorwirkung'
