# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_ref, parse_article_numbers


class DocumentReference(object):

    TAG_SOURCE = 'Ursprung'
    TAG_TARGET = 'Hinweis'
    TAG_ARTICLE_NUMBERS = 'ArtikelNr'

    def __init__(self, session, model):
        self._session = session
        self._model = model

    def parse(self, document_reference):  # pragma: no cover
        source = parse_ref(document_reference, self.TAG_SOURCE)
        target = parse_ref(document_reference, self.TAG_TARGET)
        instance = self._model(
            id='{0}-{1}'.format(source, target),
            document_id=source,
            reference_document_id=target,
            article_numbers=parse_article_numbers(
                document_reference,
                self.TAG_ARTICLE_NUMBERS
            )
        )
        self._session.add(instance)
