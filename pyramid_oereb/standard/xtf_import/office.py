# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_string, parse_multilingual_text


class Office(object):

    TAG_NAME = 'Name'
    TAG_OFFICE_AT_WEB = 'AmtImWeb'
    TAG_UID = 'UID'

    def __init__(self, session, model):
        self._session = session
        self._model = model

    def parse(self, office):  # pragma: no cover
        instance = self._model(
            id=office.attrib['TID'],
            name=parse_multilingual_text(office, self.TAG_NAME),
            office_at_web=parse_string(office, self.TAG_OFFICE_AT_WEB),
            uid=parse_string(office, self.TAG_UID)
        )
        self._session.add(instance)
