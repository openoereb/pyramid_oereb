# -*- coding: utf-8 -*-


class PlrRecord(object):
    content = None
    topic = None
    subtopic = None
    additional_topic = None
    type_code = None
    type_code_list = None
    legal_state = None
    published_from = None
    view_service = None
    basis = list()
    refinements = list()
    documents = list()
    geometries = list()

    def __init__(self, content=None, topic=None, legal_state=None, published_from=None, subtopic=None,
                 additional_topic=None, type_code=None, type_code_list=None, view_service=None, basis=list(),
                 refinements=list(), documents=list(), geometries=list()):
        """
        Public law restriction record.
        :param content:             The PLR record's content.
        :type  content:             str
        :param topic:               The topic to which the PLR belongs to.
        :type  topic:               str
        :param legal_state:         The PLR record's legal state.
        :type legal_state:          str
        :param published_from:      Date from/since when the PLR record is published.
        :type published_from:       datetime.date
        :param subtopic:            Optional subtopic.
        :type subtopic:             str
        :param additional_topic:    Optional additional topic.
        :type additional_topic:     str
        :param type_code:           The PLR record's type code (also used by view service).
        :type type_code:            str
        :param type_code_list:      URL to the PLR's list of type codes.
        :type type_code_list:       str
        :param view_service:        The view service instance associated with this record.
        :type view_service:         object
        :param basis:               List of PLR records as basis for this record.
        :type basis:                list
        :param refinements:         List of PLR records as refinement of this record.
        :type refinements:          list
        :param documents:           List of documents associated with this record.
        :type documents:            list
        :param geometries:          List of geometries associated with this record.
        :type geometries:           list
        :raises TypeError:          Raised on missing field value.
        """
        if not (content and topic and legal_state and published_from):
            raise TypeError('Fields "content", "topic", "legal_state" and "published_from" must be defined. '
                            'Got {0}, {1}, {2}, {3}.'.format(content, topic, legal_state, published_from))

        self.content = content
        self.topic = topic
        self.legal_state = legal_state
        self.published_from = published_from
        self.subtopic = subtopic
        self.additional_topic = additional_topic
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.view_service = view_service
        self.basis = basis
        self.refinements = refinements
        self.documents = documents
        self.geometries = geometries

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return:    List of available field names.
        :rtype:     list
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
