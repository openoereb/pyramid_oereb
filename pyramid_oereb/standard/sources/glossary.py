# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.glossary import GlossaryBaseSource


class DatabaseSource(BaseDatabaseSource, GlossaryBaseSource):

    def read(self):
        """
        Central method to read all glossary entries.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.title,
                    result.content
                ))
        finally:
            session.close()
