# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.glossary import GlossaryBaseSource
from pyramid_oereb.contrib.interlis.interlis_2_3_utils import from_multilingual_text_to_dict


class DatabaseSource(BaseDatabaseSource, GlossaryBaseSource):

    def read(self, params):
        """
        Central method to read all glossary entries.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    from_multilingual_text_to_dict(
                        de=result.title_de,
                        fr=result.title_fr,
                        it=result.title_it,
                        rm=result.title_rm,
                        en=result.title_en),
                    from_multilingual_text_to_dict(
                        de=result.content_de,
                        fr=result.content_fr,
                        it=result.content_it,
                        rm=result.content_rm,
                        en=result.content_en)
                ))
        finally:
            session.close()
