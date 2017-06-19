# -*- coding: utf-8 -*-
from datetime import datetime


def get_update_date_from_file():
    """
    Gets the date of the latest update of the used data from a file
    """

    return


def get_update_date_from_db():
    """
    Gets the date of the latest update of the used data from a table
    """

    return


def get_surveying_data_update_date():
    """
    Gets the date of the latest update of the used cadastral data for the
    situation map.
    """

    update_date = datetime.date.today()

    return update_date
