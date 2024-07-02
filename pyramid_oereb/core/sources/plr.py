# -*- coding: utf-8 -*-
import logging

from pyramid_oereb.core.sources import Base

log = logging.getLogger(__name__)


class PlrBaseSource(Base):
    """
    Base class for public law restriction sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.plr.EmptyPlrRecord): List of public law restriction
            records.
        datasource (list of pyramid_oereb.lib.records.embeddable.DatasourceRecord): List of data source
            records used for the additional data in flavour `embeddable`.
    """
    datasource = list()

    def __init__(self, **kwargs):
        """
        Keyword Arguments:
            name (str): The name. You are free to choose one.
            code (str): The official code. Regarding to the federal specifications.
            geometry_type (str): The geometry type. Possible are: POINT, POLYGON, LINESTRING,
                GEOMETRYCOLLECTION
            thresholds (dict): The configuration of limits and units used for processing.
            text (dict of str): The speaking title. It must be a dictionary containing language (as
                configured) as key and text as value.
            language (str): The language this public law restriction is originally shipped with.
            federal (bool): Switch if it is a federal topic. This will be taken into account in processing
                steps.
            source (dict): The configuration dictionary of the public law restriction
            hooks (dict of str): The hook methods: get_symbol, get_symbol_ref. They have to be provided as
                dotted string for further use with dotted name resolver of pyramid package.
            law_status (dict of str): The configuration dictionary of the law status. It consists of
                the code and text which must be a dictionary containing language (as configured)
                as key and text as value.
        """
        self._plr_info = kwargs

    @property
    def info(self):
        """
        Return the info dictionary.

        Returns:
            dict: The info dictionary.
        """
        return self._plr_info
