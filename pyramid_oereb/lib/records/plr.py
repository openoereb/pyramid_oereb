# -*- coding: utf-8 -*-


class PlrRecord(object):
    # Attributes added or calculated by the processor
    area = None
    part_in_percent = None
    symbol = None

    def __init__(self, content, topic, legal_state, published_from, subtopic=None,
                 additional_topic=None, type_code=None, type_code_list=None, view_service=None, basis=None,
                 refinements=None, documents=None, geometries=None):
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
        :raises TypeError: Raised on missing field value.
        """

        self.content = content
        self.topic = topic
        self.legal_state = legal_state
        self.published_from = published_from
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
            'subtopic'
        ]
