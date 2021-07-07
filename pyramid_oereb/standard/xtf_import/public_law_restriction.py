# -*- coding: utf-8 -*-
from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard.xtf_import.util import parse_string, parse_multilingual_text, parse_ref


class PublicLawRestriction(object):

    TAG_LEGEND_TEXT = 'Aussage'
    TAG_SUB_THEME = 'SubThema'
    TAG_TYPE_CODE = 'ArtCode'
    TAG_TYPE_CODE_LIST = 'ArtCodeliste'
    TAG_LAW_STATUS = 'Rechtsstatus'
    TAG_PUBLISHED_FROM = 'publiziertAb'
    TAG_VIEW_SERVICE = 'DarstellungsDienst'
    TAG_RESPONSIBLE_OFFICE = 'ZustaendigeStelle'

    def __init__(self, session, model, topic_code):
        self._session = session
        self._model = model
        self._topic_code = topic_code

    def parse(self, public_law_restriction):  # pragma: no cover
        language = Config.get('default_language')
        sub_theme = parse_string(public_law_restriction, self.TAG_SUB_THEME)
        if sub_theme is not None:
            sub_theme = {language: sub_theme}
        instance = self._model(
            id=public_law_restriction.attrib['TID'],
            legend_text=parse_multilingual_text(public_law_restriction, self.TAG_LEGEND_TEXT),
            topic=self._topic_code,
            sub_theme=sub_theme,
            type_code=parse_string(public_law_restriction, self.TAG_TYPE_CODE),
            type_code_list=parse_string(public_law_restriction, self.TAG_TYPE_CODE_LIST),
            law_status=parse_string(public_law_restriction, self.TAG_LAW_STATUS),
            published_from=parse_string(public_law_restriction, self.TAG_PUBLISHED_FROM),
            view_service_id=parse_ref(public_law_restriction, self.TAG_VIEW_SERVICE),
            office_id=parse_ref(public_law_restriction, self.TAG_RESPONSIBLE_OFFICE)
        )
        self._session.add(instance)
