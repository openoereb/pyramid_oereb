# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_string, parse_multilingual_text, parse_ref


class Document(object):

    TAG_TEXT_AT_WEB = 'TextImWeb'
    TAG_LAW_STATUS = 'Rechtsstatus'
    TAG_PUBLISHED_FROM = 'publiziertAb'
    TAG_TITLE = 'Titel'
    TAG_OFFICIAL_TITLE = 'OffiziellerTitel'
    TAG_ABBREVIATION = 'Abkuerzung'
    TAG_OFFICIAL_NUMBER = 'OffizielleNr'
    TAG_RESPONSIBLE_OFFICE = 'ZustaendigeStelle'

    def __init__(self, session, model):
        self._session = session
        self._model = model

    def parse(self, document, document_type):  # pragma: no cover
        instance = self._model(
            id=document.attrib['TID'],
            text_at_web=parse_multilingual_text(document, self.TAG_TEXT_AT_WEB),
            law_status=parse_string(document, self.TAG_LAW_STATUS),
            published_from=parse_string(document, self.TAG_PUBLISHED_FROM),
            document_type=document_type,
            title=parse_multilingual_text(document, self.TAG_TITLE),
            official_title=parse_multilingual_text(document, self.TAG_OFFICIAL_TITLE),
            abbreviation=parse_multilingual_text(document, self.TAG_ABBREVIATION),
            official_number=parse_string(document, self.TAG_OFFICIAL_NUMBER),
            office_id=parse_ref(document, self.TAG_RESPONSIBLE_OFFICE)
        )
        self._session.add(instance)
