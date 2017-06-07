# -*- coding: utf-8 -*-


class AvailabilityRecord(object):

    def __init__(self, fosnr, available=False):
        """
        The record to check if data is available for municipality.

        :param fosnr: The unique id of the municipality.
        :type fosnr: int
        :param available: Switch if data is available in municipality or not.
        :type available: bool
        """
        self.fosnr = fosnr
        self.available = available
