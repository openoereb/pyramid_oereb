# -*- coding: utf-8 -*-


class AvailabilityRecord(object):

    def __init__(self, fosnr, theme_code, available=False):
        """
        The record to check if data is available for municipality.

        Args:
            fosnr (int): The unique id of the municipality.
            theme_code (str): The theme_code which is affected to be available or not.
            available (bool): Switch if data is available in municipality and theme/sub theme or not.
        """
        self.fosnr = fosnr
        self.theme_code = theme_code
        self.available = available
