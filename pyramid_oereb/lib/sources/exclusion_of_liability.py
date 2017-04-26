# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord


class ExclusionOfLiabilityBaseSource(Base):
    _record_class_ = ExclusionOfLiabilityRecord

    def read(self):
        pass  # pragma: no cover


class ExclusionOfLiabilityDatabaseSource(BaseDatabaseSource, ExclusionOfLiabilityBaseSource):

    def read(self):
        """
        Central method to read a exclusion of liability definition.
        """
        session = self._adapter_.get_session(self._key_)
        results = session.query(self._model_).all()

        self.records = list()
        for result in results:
            self.records.append(self._record_class_(
                result.title,
                result.content
            ))

        session.close()
