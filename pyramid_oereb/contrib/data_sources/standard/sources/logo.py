# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.logo import LogoBaseSource


class DatabaseSource(BaseDatabaseSource, LogoBaseSource):

    def read(self):
        """
        Central method to read all logos.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.code,
                    result.logo
                ))
        finally:
            session.close()
