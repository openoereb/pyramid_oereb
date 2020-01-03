# -*- coding: utf-8 -*-

"""
This package is meant for contributions to the project, that are not part of the core libraries but may be
useful in general.
"""
import logging

from functools import cmp_to_key


log = logging.getLogger(__name__)


def plr_sort_within_themes_by_type_code(extract):
    """
    This is the standard hook method to sort a plr list (while respecting the theme order.
    This standard hook does no sorting, you can set your configuration to a different method if you need a
    specific sorting.

    Args:
        extract

    Returns:
        The sorted extract
    """
    real_estate = extract.real_estate

    if log.isEnabledFor(logging.DEBUG):
        for public_law_restriction in real_estate.public_law_restrictions:
            log.debug("START plr_sort_within_themes_by_type_code: plr theme {}, type_code {}".
                      format(public_law_restriction.theme.code, public_law_restriction.type_code))

    def cmp(a, b):
        if a.theme.code == b.theme.code:
            value_a = a.type_code
            value_b = b.type_code
            if value_a < value_b:
                ret = -1
            elif value_a == value_b:
                ret = 0
            else:
                ret = 1
        else:
            ret = 0
        return ret

    real_estate.public_law_restrictions = sorted(real_estate.public_law_restrictions, key=cmp_to_key(cmp))

    if log.isEnabledFor(logging.DEBUG):
        for public_law_restriction in real_estate.public_law_restrictions:
            log.debug("DONE plr_sort_within_themes_by_type_code: plr theme {}, type_code {}".
                      format(public_law_restriction.theme.code, public_law_restriction.type_code))

    return extract
