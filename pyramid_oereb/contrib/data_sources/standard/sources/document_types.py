# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.document_types import DocumentTypesBaseSource


class DatabaseSource(BaseDatabaseSource, DocumentTypesBaseSource):

    def read(self):
        """
        Central method to read all document type values.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            records = list()
            for result in results:
                records.append(self._record_class_(
                    result.code,
                    result.title
                ))
            return records
        finally:
            session.close()
