# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_ref


class DocumentReferenceDefinition(object):

    TAG_DOCUMENT = 'Dokument'
    TAG_REFERENCE_DEFINITION = 'HinweisDefinition'

    def __init__(self, session, model):
        self._session = session
        self._model = model

    def parse(self, document_reference_definition):  # pragma: no cover
        document_id = parse_ref(document_reference_definition, self.TAG_DOCUMENT)
        reference_definition_id = parse_ref(document_reference_definition, self.TAG_REFERENCE_DEFINITION)
        instance = self._model(
            id='{0}-{1}'.format(document_id, reference_definition_id),
            document_id=document_id,
            reference_definition_id=reference_definition_id
        )
        self._session.add(instance)
