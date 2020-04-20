# -*- coding: utf-8 -*-
from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard.xtf_import.util import parse_string

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse


class ViewService(object):

    TAG_REFERENCE_WMS = 'VerweisWMS'
    TAG_LEGEND_AT_WEB = 'LegendeImWeb'
    TAG_LEGEND = 'Legende'

    def __init__(self, session, model, legend_entry):
        self._session = session
        self._model = model
        self._legend_entry = legend_entry

    def parse(self, view_service):  # pragma: no cover
        reference_wms = parse_string(view_service, self.TAG_REFERENCE_WMS)
        language = Config.get('default_language')
        legend_at_web = parse_string(view_service, self.TAG_LEGEND_AT_WEB)
        if legend_at_web is not None:
            legend_at_web = {
                language: legend_at_web
            }
        if legend_at_web is None and reference_wms is not None:
            legend_at_web = {
                language: self._copy_legend_at_web_from_reference_wms(reference_wms)
            }
        instance = self._model(
            id=view_service.attrib['TID'],
            reference_wms=reference_wms,
            legend_at_web=legend_at_web
        )
        self._session.add(instance)
        self._legend_entry.parse(view_service)

    @staticmethod
    def _copy_legend_at_web_from_reference_wms(reference_wms):
        url = urlparse.urlparse(reference_wms)
        query = urlparse.parse_qs(url.query)
        for param in ['STYLES', 'WIDTH', 'HEIGHT', 'SRS', 'BBOX']:
            if param in query:
                query.pop(param)
        query.update({
            'REQUEST': ['GetLegendGraphic'],
            'LAYER': query.pop('LAYERS')
        })
        for key in query:
            query[key] = query[key][0]
        if query.get('VERSION') == '1.3.0':
            query.update({
                'SLD_VERSION': '1.1.0'
            })
        return urlparse.urlunparse((
            url.scheme,
            url.netloc,
            url.path,
            url.params,
            urlencode(query),
            url.fragment
        ))
