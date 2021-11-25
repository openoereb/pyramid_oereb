# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.office import OfficeBaseSource


class DatabaseSource(BaseDatabaseSource, OfficeBaseSource):

    def read(self):
        """
        Central method to read all office entries.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.name,
                    result.uid,
                    result.office_at_web,
                    result.line1,
                    result.line2,
                    result.street,
                    result.number,
                    result.postal_code,
                    result.city,
                    identifier=result.id
                ))
        finally:
            session.close()
