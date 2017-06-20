# -*- coding: utf-8 -*-
from datetime import date


def get_update_date_from_file():
    """
    Gets the date of the latest update of the used data from a file
    """
    # TODO: Decide if there should be a general method to read the date either from
    # a file or a db table and for one date or multiple dates in f(e.g municipality)
    return


def get_update_date_from_db():
    """
    Gets the date of the latest update of the used data from a table
    """
    # TODO: Decide if there should be a general method to read the date either from
    # a file or a db table and for one date or multiple dates in f(e.g municipality)
    return


def get_surveying_data_update_date(real_estate):
    """
    Gets the date of the latest update of the used cadastral data for the
    situation map.

    Args:
        real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
            estate for which the last update date of the base data should be indicated

    Returns:
        update_date (datetime.date): The date of the last update of the cadastral base data
    """

    update_date = date.today()

    return update_date
