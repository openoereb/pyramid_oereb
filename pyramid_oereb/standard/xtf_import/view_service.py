# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_multilingual_text


class ViewService(object):

    TAG_REFERENCE_WMS = 'VerweisWMS'
    TAG_LEGEND = 'Legende'

    def __init__(self, session, model, legend_entry):
        self._session = session
        self._model = model
        self._legend_entry = legend_entry

    def parse(self, view_service):  # pragma: no cover
        reference_wms = parse_multilingual_text(view_service, self.TAG_REFERENCE_WMS)
        instance = self._model(
            id=view_service.attrib['TID'],
            reference_wms=reference_wms
        )
        self._session.add(instance)
        self._legend_entry.parse(view_service)
