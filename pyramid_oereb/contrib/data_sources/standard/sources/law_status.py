from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.law_status import LawStatusBaseSource


class DatabaseSource(BaseDatabaseSource, LawStatusBaseSource):

    def read(self, params=None):
        """
        Central method to read all law status values.
        Args:
            params (pyramid_oereb.views.webservice.Parameter or None): The parameters of the extract request.
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
