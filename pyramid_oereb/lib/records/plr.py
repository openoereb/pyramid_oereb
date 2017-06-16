# -*- coding: utf-8 -*-
import warnings
from datetime import datetime


class EmptyPlrRecord(object):

    def __init__(self, theme, has_data=True):
        """
        Record for empty topics.

        Args:
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
            has_data (bool): True if the topic contains data.
        """
        self.theme = theme
        self.has_data = has_data


class PlrRecord(EmptyPlrRecord):

    # Attributes added or calculated by the processor
    area = None
    """decimal: Area of the restriction touching the property calculated by the processor."""

    part_in_percent = None
    """decimal: Part of the property area touched by the restriction in percent."""

    symbol = None
    """binary or None: Symbol of the restriction defined for the legend entry - added on the fly."""

    def __init__(self, theme, content, legal_state, published_from, responsible_office, subtopic=None,
                 additional_topic=None, type_code=None, type_code_list=None, view_service=None, basis=None,
                 refinements=None, documents=None, geometries=None, info=None):
        """
        Public law restriction record.

        Args:
            content (dict of unicode): The PLR record's content (multilingual).
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
            legal_state (unicode): The PLR record's legal state.
            published_from (datetime.date): Date from/since when the PLR record is published.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is responsible
                for this PLR.
            subtopic (unicode): Optional subtopic.
            additional_topic (unicode): Optional additional topic.
            type_code (unicode): The PLR record's type code (also used by view service).
            type_code_list (unicode): URL to the PLR's list of type codes.
            view_service (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service instance
                associated with this record.
            basis (list of PlrRecord): List of PLR records as basis for this record.
            refinements (list of PlrRecord): List of PLR records as refinement of this record.
            documents (list of pyramid_oereb.lib.records.documents.DocumentBaseRecord): List of documents
                associated with this record.
            geometries (list of pyramid_oereb.lib.records.geometry.GeometryRecord): List of geometry records
                associated with this record.
            info (dict or None): The information read from the config.
        """
        super(PlrRecord, self).__init__(theme)

        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict"')

        self.content = content
        self.legal_state = legal_state
        self.published_from = published_from
        self.responsible_office = responsible_office
        self.subtopic = subtopic
        self.additional_topic = additional_topic
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.view_service = view_service
        if basis is None:
            self.basis = []
        else:
            self.basis = basis
        if refinements is None:
            self.refinements = []
        else:
            self.refinements = refinements
        if documents is None:
            self.documents = []
        else:
            self.documents = documents
        if geometries is None:
            self.geometries = []
        else:
            self.geometries = geometries
        self.info = info
        self.has_data = True

    @property
    def published(self):
        """bool: True if PLR is published."""
        return not self.published_from > datetime.now().date()
