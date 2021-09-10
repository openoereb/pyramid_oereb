# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.theme import ThemeBaseSource
from pyramid_oereb.contrib.interlis.interlis_2_3_utils import from_multilingual_text_to_dict


class DatabaseSource(BaseDatabaseSource, ThemeBaseSource):

    def read(self):
        """
        Central method to read all theme entries.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.code,
                    from_multilingual_text_to_dict(
                        de=result.title_de,
                        fr=result.title_fr,
                        it=result.title_it,
                        rm=result.title_rm,
                        en=result.title_en),
                    result.extract_index
                ))
        finally:
            session.close()
