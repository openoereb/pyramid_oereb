# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord


class ExclusionOfLiabilityBaseSource(Base):
    _record_class_ = ExclusionOfLiabilityRecord

    def read(self, id, title, content):
        pass  # pragma: no cover


class ExclusionOfLiabilityDatabaseSource(BaseDatabaseSource, ExclusionOfLiabilityBaseSource):

    def read(self, id, title, content):
        """
        Central method to read a exclusion of liability definition.
        """
        session = self._adapter_.get_session(self._key_)
        results = session.query(self._model_).filter(self._model_.id==id).one()

        self.records = list()
        for result in results:
            self.records.append(self._record_class_(
                result.id,
                result.title,
                result.content
            ))
