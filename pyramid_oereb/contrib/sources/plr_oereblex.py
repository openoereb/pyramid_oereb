# -*- coding: utf-8 -*-
import logging

from pyramid_oereb import Config
from pyramid_oereb.contrib.sources.document import OEREBlexSource
from pyramid_oereb.standard.sources.plr import DatabaseSource

log = logging.getLogger(__name__)


class DatabaseOEREBlexSource(DatabaseSource):
    """
    A source to get oereblex documents attached to public law restrictions in replacement
    of standards documents. Be sure to use a model with an OEREBlex "lexlink" integer
    column for plrs that use this source.
    """
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
            law_status (dict of str): The multiple match configuration to provide more flexible use of the
                federal specified classifiers 'inForce' and 'runningModifications'.
        """
        super(DatabaseOEREBlexSource, self).__init__(**kwargs)
        self._oereblex_source = OEREBlexSource(**Config.get_oereblex_config())

    def get_document_records(self, public_law_restriction_from_db):
        """
        Override the parent's get_document_records method to obtain the oereblex document instead.
        """
        return self.document_records_from_oereblex(public_law_restriction_from_db.geolink)

    def document_records_from_oereblex(self, lexlink):
        """
        Create document records parsed from the OEREBlex response with the specified geoLink ID and appends
        them to the current public law restriction.

        Args:
            lexlink (int): The ID of the geoLink to request the documents for.

        Returns:
            list of pyramid_oereb.lib.records.documents.DocumentRecord:
                The documents created from the parsed OEREBlex response.
        """
        log.debug("document_records_from_oereblex() start")
        self._oereblex_source.read(lexlink)
        log.debug("document_records_from_oereblex() returning records")
        return self._oereblex_source.records
