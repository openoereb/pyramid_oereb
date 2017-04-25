# -*- coding: utf-8 -*-


class EmptyPlrRecord(object):

    def __init__(self, topic):
        self.topic = topic
        self.affected = False

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'topic',
            'affected'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in [
            'topic'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value
        extract['affected'] = self.affected
        return extract


class PlrRecord(EmptyPlrRecord):
    # Attributes added or calculated by the processor
    area = None
    part_in_percent = None
    symbol = None

    def __init__(self, topic, content, legal_state, published_from, responsible_office, subtopic=None,
                 additional_topic=None, type_code=None, type_code_list=None, view_service=None, basis=None,
                 refinements=None, documents=None, geometries=None, info=None, affected=True):
        """
        Public law restriction record.
        :param content: The PLR record's content.
        :type  content: str
        :param topic: The topic to which the PLR belongs to.
        :type  topic: str
        :param legal_state: The PLR record's legal state.
        :type legal_state: str
        :param published_from: Date from/since when the PLR record is published.
        :type published_from: datetime.date
        :param responsible_office: Office which is responsible for this PLR.
        :type responsible_office: pyramid_oereb.lib.records.office.OfficeRecord
        :param subtopic: Optional subtopic.
        :type subtopic: str
        :param additional_topic: Optional additional topic.
        :type additional_topic: str
        :param type_code: The PLR record's type code (also used by view service).
        :type type_code: str
        :param type_code_list: URL to the PLR's list of type codes.
        :type type_code_list: str
        :param view_service: The view service instance associated with this record.
        :type view_service: pyramid_oereb.lib.records.view_service.ViewServiceRecord
        :param basis: List of PLR records as basis for this record.
        :type basis: list of PlrRecord
        :param refinements: List of PLR records as refinement of this record.
        :type refinements: list of PlrRecord
        :param documents: List of documents associated with this record.
        :type documents: list of pyramid_oereb.lib.records.documents.DocumentBaseRecord
        :param geometries: List of geometries (shapely) associated with this record.
        :type geometries: list of shapely.geometry.base.BaseGeometry
        :param area: Area of the restriction touching the property calculated by the processor.
        :type area: decimal
        :param part_in_percent: Part of the property area touched by the restriction in percent.
        :type part_in_percent: decimal
        :param symbol: Symbol of the restriction defined for the legend entry - added on the fly.
        :type symbol: binary
        :param info: The information read from the config
        :type info: dict or None
        :param affected: Switch to provide easy access and more easy handling
        :type affected: bool
        :raises TypeError: Raised on missing field value.
        """

        super(PlrRecord, self).__init__(topic)
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
        self.affected = affected

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'topic',
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
            'topic',
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
        key = 'responsible_office'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract()
        key = 'view_service'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract(type_code=self.type_code)
        extract['affected'] = self.affected
        return extract
