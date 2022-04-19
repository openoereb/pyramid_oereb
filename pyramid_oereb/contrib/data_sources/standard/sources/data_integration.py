
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.data_integration import DataIntegrationRecord


class DatabaseSource(BaseDatabaseSource, DataIntegrationRecord):

    def read(self):
        """
        The read method to access the standard database structure. It uses SQL-Alchemy for querying. It does
        not accept any parameters nor it applies any filter on the database query. It simply loads all
        content from the configured model.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.date,
                    result.checksum,
                    result.available
                ))
        finally:
            session.close()
