
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.data_integration import DataIntegrationBaseSource


class DatabaseSource(BaseDatabaseSource, DataIntegrationBaseSource):

    def read(self):
        """
        The read method to access the standard database structure. It uses SQL-Alchemy for querying. It does
        not accept any parameters nor it applies any filter on the database query. It simply loads all
        content from the configured model.

        Returns:
            list of pyramid_oereb.core.records.data_integration.DataIntegrationRecord: The list of
                data_integration records.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            records = list()
            for result in results:
                records.append(self._record_class_(
                    result.date,
                    checksum=result.checksum,
                    theme_identifier=result.theme_code,
                    office_identifier=result.office_id
                ))
            return records
        finally:
            session.close()
