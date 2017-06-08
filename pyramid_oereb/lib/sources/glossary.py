# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.glossary import GlossaryRecord


class GlossaryBaseSource(Base):
    _record_class_ = GlossaryRecord

    def read(self):
        pass  # pragma: no cover


class GlossaryDatabaseSource(BaseDatabaseSource, GlossaryBaseSource):

    def read(self):
        """
        Central method to read a glossary entry.

        Args:
            id (int): The identifier in the database
            title (unicode): The term used in the extract
            content (unicode): The description text for the glossary entry.
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
