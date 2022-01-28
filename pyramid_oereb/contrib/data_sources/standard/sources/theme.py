# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.theme import ThemeBaseSource


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
                    result.title,
                    result.extract_index,
                    result.sub_code,
                    identifier=result.id
                ))
        finally:
            session.close()
