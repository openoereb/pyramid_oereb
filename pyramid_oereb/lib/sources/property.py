# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource


class PropertyDatabaseSource(BaseDatabaseSource):

    def read(self, key):
        """
        Central method to read all plrs.
        :param key: Key of the desired database connection
        :type key: str
        """
        session = self._adapter_.get_session(self._key_)
        results = session.query(self._model_).all()
        self.records = list()
        # TODO: Assign all found values from database record to internal record.
