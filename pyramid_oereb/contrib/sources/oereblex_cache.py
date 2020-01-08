# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


class OEREBlexCache(object):
    """
    A cache for Oereblex records
    """
    _cache_dict = {}

    @staticmethod
    def get_records(lexlink):
        """
        Returns the records for a specified lexlink, if they are in the cache
        """
        records = OEREBlexCache._cache_dict.get(lexlink)
        if records:
            log.debug("CACHE HIT on lexlink {} return {} records from cache".format(lexlink, len(records)))
        else:
            log.debug("CACHE MISS on lexlink {}".format(lexlink))
        return records

    @staticmethod
    def add_records(lexlink, records):
        """
        Add records for a given lexlink
        """
        if records:
            log.debug("CACHE putting lexlink {}, with {} records".format(lexlink, len(records)))
            OEREBlexCache._cache_dict[lexlink] = records
        else:
            log.debug("CACHE called with null records for lexlink {}, ignoring".format(lexlink))
