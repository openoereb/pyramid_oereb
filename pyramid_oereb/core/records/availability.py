# -*- coding: utf-8 -*-


class AvailabilityRecord(object):
    """
    The record to check if data is available for municipality.

    Args:
        fosnr (int): The unique id of the municipality.
        available (bool): Switch if data is available in municipality or not.
    """
    def __init__(self, fosnr, available=False):
        self.fosnr = fosnr
        self.available = available
