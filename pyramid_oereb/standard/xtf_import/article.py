# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_string, parse_multilingual_text, parse_ref


class Article(object):

    TAG_TEXT_AT_WEB = 'TextImWeb'
    TAG_LAW_STATUS = 'Rechtsstatus'
    TAG_PUBLISHED_FROM = 'publiziertAb'
    TAG_NUMBER = 'Nr'
    TAG_TEXT = 'Text'
    TAG_DOCUMENT = 'Dokument'

    def __init__(self, session, model):
        self._session = session
        self._model = model

    def parse(self, article):  # pragma: no cover
        instance = self._model(
            id=article.attrib['TID'],
            text_at_web=parse_multilingual_text(article, self.TAG_TEXT_AT_WEB),
            law_status=parse_string(article, self.TAG_LAW_STATUS),
            published_from=parse_string(article, self.TAG_PUBLISHED_FROM),
            number=parse_string(article, self.TAG_NUMBER),
            text=parse_multilingual_text(article, self.TAG_TEXT),
            document_id=parse_ref(article, self.TAG_DOCUMENT)
        )
        self._session.add(instance)
