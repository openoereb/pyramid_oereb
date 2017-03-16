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
        :param content:
        :type content: str
        :param topic:
        :param legal_state:
        :param published_from:
        :param subtopic:
        :param additional_topic:
        :param type_code:
        :param type_code_list:
        :param view_service:
        :param basis:
        :param refinements:
        :param documents:
        :param geometries:
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
