# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_ref, parse_article_numbers


class PublicLawRestrictionDocument(object):

    TAG_SOURCE = 'Eigentumsbeschraenkung'
    TAG_TARGET = 'Vorschrift'
    TAG_ARTICLE_NUMBERS = 'ArtikelNr'

    def __init__(self, session, model):
        self._session = session
        self._model = model

    def parse(self, plr_document):  # pragma: no cover
        source = parse_ref(plr_document, self.TAG_SOURCE)
        target = parse_ref(plr_document, self.TAG_TARGET)
        instance = self._model(
            id='{0}-{1}'.format(source, target),
            public_law_restriction_id=source,
            document_id=target,
            article_numbers=parse_article_numbers(
                plr_document,
                self.TAG_ARTICLE_NUMBERS
            )
        )
        self._session.add(instance)
