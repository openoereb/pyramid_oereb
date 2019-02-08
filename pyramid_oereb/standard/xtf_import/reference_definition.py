# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_string, parse_ref


class ReferenceDefinition(object):

    TAG_CANTON = 'Kanton'
    TAG_MUNICIPALITY = 'Gemeinde'
    TAG_RESPONSIBLE_OFFICE = 'ZustaendigeStelle'

    def __init__(self, session, model, topic_code):
        self._session = session
        self._model = model
        self._topic_code = topic_code

    def parse(self, reference_definition):  # pragma: no cover
        instance = self._model(
            id=reference_definition.attrib['TID'],
            topic=self._topic_code,
            canton=parse_string(reference_definition, self.TAG_CANTON),
            municipality=parse_string(reference_definition, self.TAG_MUNICIPALITY),
            office_id=parse_ref(reference_definition, self.TAG_RESPONSIBLE_OFFICE)
        )
        self._session.add(instance)
