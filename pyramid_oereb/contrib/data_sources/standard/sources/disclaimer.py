# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.disclaimer import DisclaimerBaseSource


class DatabaseSource(BaseDatabaseSource, DisclaimerBaseSource):

    def read(self):
        """
        The read method to access the standard database structure. It uses SQL-Alchemy for querying. It does
        not accept any parameters nor it applies any filter on the database query. It simply loads all
        content from the configured model.

        Returns:
            list of pyramid_oereb.core.records.disclaimer.DisclaimerRecord: The list of disclaimer
                records.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            records = list()
            for result in results:
                records.append(self._record_class_(
                    result.title,
                    result.content,
                    result.extract_index
                ))
            return records
        finally:
            session.close()
