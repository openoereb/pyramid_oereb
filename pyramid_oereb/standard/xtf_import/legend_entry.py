# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_string, parse_multilingual_text, get_tag


class LegendEntry(object):

    TAG_LEGEND = 'Legende'
    TAG_LEGEND_ENTRY = 'OeREBKRMtrsfr_V1_1.Transferstruktur.LegendeEintrag'
    TAG_SYMBOL = 'Symbol'
    TAG_SYMBOL_BIN = 'BINBLBOX'
    TAG_LEGEND_TEXT = 'LegendeText'
    TAG_TYPE_CODE = 'ArtCode'
    TAG_TYPE_CODE_LIST = 'ArtCodeliste'
    TAG_SUB_THEME = 'SubThema'
    TAG_OTHER_THEME = 'WeiteresThema'

    def __init__(self, session, model, topic_code):
        self._session = session
        self._model = model
        self._topic_code = topic_code

    def parse(self, view_service):  # pragma: no cover
        for element in view_service:
            if get_tag(element) == self.TAG_LEGEND:
                count = 1
                for legend_entry in element:
                    if get_tag(legend_entry) == self.TAG_LEGEND_ENTRY:
                        instance = self._model(
                            id='{0}.legende.{1}'.format(view_service.attrib['TID'], count),
                            symbol=self._parse_symbol(legend_entry, self.TAG_SYMBOL),
                            legend_text=parse_multilingual_text(
                                legend_entry,
                                self.TAG_LEGEND_TEXT
                            ),
                            type_code=parse_string(legend_entry, self.TAG_TYPE_CODE),
                            type_code_list=parse_string(
                                legend_entry,
                                self.TAG_TYPE_CODE_LIST
                            ),
                            topic=self._topic_code,
                            sub_theme=parse_string(legend_entry, self.TAG_SUB_THEME),
                            other_theme=parse_string(legend_entry, self.TAG_OTHER_THEME),
                            view_service_id=view_service.attrib['TID']
                        )
                        self._session.add(instance)
                        count += 1

    def _parse_symbol(self, element, prop):
        for p in element:
            if get_tag(p) == prop:
                for binblbox in p:
                    if get_tag(binblbox) == self.TAG_SYMBOL_BIN:
                        return binblbox.text
        return None
