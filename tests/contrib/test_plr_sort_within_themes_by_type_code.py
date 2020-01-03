# -*- coding: utf-8 -*-
import logging
import pytest

from pyramid_oereb.contrib import plr_sort_within_themes_by_type_code
from tests.records.test_extract import create_dummy_extract
from tests.records.test_plr import create_dummy_plr


log = logging.getLogger(__name__)


@pytest.mark.run(order=2)
def test_sort():
    extract = create_dummy_extract()
    real_estate = extract.real_estate
    plr1 = create_dummy_plr()
    plr1.theme.code = "LandUsePlans"
    plr1.type_code = "Zebra"

    plr2 = create_dummy_plr()
    plr2.theme.code = "LandUsePlans"
    plr2.type_code = "Belize"

    plr3 = create_dummy_plr()
    plr3.theme.code = "LandUsePlans"
    plr3.type_code = "Dingo"

    plr4 = create_dummy_plr()
    plr4.theme.code = "ForestDistanceLines"
    plr4.type_code = "Arboretum"

    real_estate.public_law_restrictions.append(plr1)
    real_estate.public_law_restrictions.append(plr2)
    real_estate.public_law_restrictions.append(plr3)
    real_estate.public_law_restrictions.append(plr4)

    sorted_extract = plr_sort_within_themes_by_type_code(extract)
    sorted_real_estate = sorted_extract.real_estate

    plr = sorted_real_estate.public_law_restrictions[0]
    assert plr.theme.code == "LandUsePlans" and plr.type_code == "Belize"
    plr = sorted_real_estate.public_law_restrictions[1]
    assert plr.theme.code == "LandUsePlans" and plr.type_code == "Dingo"
    plr = sorted_real_estate.public_law_restrictions[2]
    assert plr.theme.code == "LandUsePlans" and plr.type_code == "Zebra"
    plr = sorted_real_estate.public_law_restrictions[3]
    assert plr.theme.code == "ForestDistanceLines" and plr.type_code == "Arboretum"
