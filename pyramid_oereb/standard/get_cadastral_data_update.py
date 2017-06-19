# -*- coding: utf-8 -*-
from datetime import datetime

def get_surveying_data_update_date():
    """
    Gets the date of the latest update of the used cadastral data for the
    situation map.
    """

    update_date = datetime.now().strftime("%d.%m.%Y-%H:%M:%S")

    return update_date