# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_integer, parse_string, parse_multilingual_text, \
    parse_ref


class Document(object):

    TAG_TYPE = 'Typ'
    TAG_TITLE = 'Titel'
    TAG_ABBREVIATION = 'Abkuerzung'
    TAG_OFFICIAL_NUMBER = 'OffizielleNr'
    TAG_ONLY_IN_MUNICIPALITY = 'NurInGemeinde'
    TAG_TEXT_AT_WEB = 'TextImWeb'
    TAG_FILE = 'Dokument'
    TAG_INDEX = 'AuszugIndex'
    TAG_LAW_STATUS = 'Rechtsstatus'
    TAG_PUBLISHED_FROM = 'publiziertAb'
    TAG_PUBLISHED_UNTIL = 'publiziertBis'
    TAG_RESPONSIBLE_OFFICE = 'ZustaendigeStelle'

    def __init__(self, session, model):
        self._session = session
        self._model = model

    def parse(self, document):  # pragma: no cover
        instance = self._model(
            id=document.attrib['TID'],
            document_type=parse_string(document, self.TAG_TYPE),
            title=parse_multilingual_text(document, self.TAG_TITLE),
            abbreviation=parse_multilingual_text(document, self.TAG_ABBREVIATION),
            official_number=parse_multilingual_text(document, self.TAG_OFFICIAL_NUMBER),
            only_in_municipality=parse_integer(document, self.TAG_ONLY_IN_MUNICIPALITY),
            text_at_web=parse_multilingual_text(document, self.TAG_TEXT_AT_WEB),
            index=parse_integer(document, self.TAG_INDEX),
            law_status=parse_string(document, self.TAG_LAW_STATUS),
            published_from=parse_string(document, self.TAG_PUBLISHED_FROM),
            published_until=parse_string(document, self.TAG_PUBLISHED_UNTIL),
            office_id=parse_ref(document, self.TAG_RESPONSIBLE_OFFICE)
        )
        self._session.add(instance)
