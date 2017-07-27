# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.exclusion_of_liability import ExclusionOfLiabilityBaseSource


class DatabaseSource(BaseDatabaseSource, ExclusionOfLiabilityBaseSource):

    def read(self):
        """
        Central method to read a exclusion of liability definition.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.title,
                    result.content
                ))

        except:
            raise

        finally:
            session.close()
