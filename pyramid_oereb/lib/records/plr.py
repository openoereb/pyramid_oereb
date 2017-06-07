# -*- coding: utf-8 -*-
from datetime import datetime


class EmptyPlrRecord(object):

    def __init__(self, theme, has_data=True):
        """
        Record for empty topics.

        Args:
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR
                belongs to.
            has_data (bool): True if the topic contains data.
        """
        self.theme = theme
        self.has_data = has_data

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'theme',
            'has_data'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in [
            'theme'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value
        extract['has_data'] = self.has_data
        return extract


class PlrRecord(EmptyPlrRecord):
    # Attributes added or calculated by the processor
    area = None
    part_in_percent = None
    symbol = None

    def __init__(self, theme, content, legal_state, published_from, responsible_office, subtopic=None,
                 additional_topic=None, type_code=None, type_code_list=None, view_service=None, basis=None,
                 refinements=None, documents=None, geometries=None, info=None):
        """
        Public law restriction record.

        Args:
            content (str): The PLR record's content.
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR
                belongs to.
            legal_state (str): The PLR record's legal state.
            published_from (datetime.date): Date from/since when the PLR record is published.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is
                responsible for this PLR.
            subtopic (str): Optional subtopic.
            additional_topic (str): Optional additional topic.
            type_code (str): The PLR record's type code (also used by view service).
            type_code_list (str): URL to the PLR's list of type codes.
            view_service (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view
                service instance associated with this record.
            basis (listofPlrRecord): List of PLR records as basis for this record.
            refinements (listofPlrRecord): List of PLR records as refinement of this record.
            documents (listofpyramid_oereb.lib.records.documents.DocumentBaseRecord): List of
                documents associated with this record.
            geometries (listofpyramid_oereb.lib.records.geometry.GeometryRecord): List of
                geometry records associated with this record.
            area (decimal): Area of the restriction touching the property calculated by the
                processor.
            part_in_percent (decimal): Part of the property area touched by the restriction in
                percent.
            symbol (binary): Symbol of the restriction defined for the legend entry - added on
                the fly.
            info (dictorNone): The information read from the config
        :raises TypeError: Raised on missing field value.
        """

        super(PlrRecord, self).__init__(theme)
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
        """
        Returns true if its not a future PLR.
        :return: True if PLR is published.
        :rtype: bool
        """
        return not self.published_from > datetime.now().date()

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'theme',
            'documents',
            'geometries',
            'view_service',
            'refinements',
            'additional_topic',
            'content',
            'type_code_list',
            'type_code',
            'basis',
            'published_from',
            'legal_state',
            'subtopic',
            'responsible_office'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in [
            'content',
            'subtopic',
            'additional_topic',
            'type_code',
            'type_code_list',
            'legal_state',
            'area',
            'part_in_percent',
            'symbol'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value
        for key in [
            'geometries',
            'documents'
        ]:
            records = getattr(self, key)
            if records and len(records) > 0:
                extract[key] = [record.to_extract() for record in records]
        for key in [
            'theme',
            'responsible_office'
        ]:
            record = getattr(self, key)
            if record:
                extract[key] = record.to_extract()
        key = 'view_service'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract(type_code=self.type_code)
        return extract
