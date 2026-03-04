# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.glossary import GlossaryBaseSource


class DatabaseSource(BaseDatabaseSource, GlossaryBaseSource):

    def read(self):
        """
        Central method to read all glossary entries.

        Returns:
            list of pyramid_oereb.core.records.glossary.GlossaryRecord: The list of glossary records.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            records = list()
            for result in results:
                records.append(self._record_class_(
                    result.title,
                    result.content
                ))
            return records
        finally:
            session.close()
