from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.real_estate_type import RealEstateTypeBaseSource


class DatabaseSource(BaseDatabaseSource, RealEstateTypeBaseSource):

    def read(self, params=None):
        """
        Central method to read all real estate type values.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.code,
                    result.title
                ))
        finally:
            session.close()
