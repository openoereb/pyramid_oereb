# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.theme_document import ThemeDocumentBaseSource


class DatabaseSource(BaseDatabaseSource, ThemeDocumentBaseSource):

    def read(self):
        """
        Central method to read all theme document entries.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            records = list()
            for result in results:
                records.append(self._record_class_(
                    result.theme_id,
                    result.document_id,
                    result.article_numbers
                ))
            return records
        finally:
            session.close()
