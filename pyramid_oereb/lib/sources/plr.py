# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.sources import Base


class PlrBaseSource(Base):

    def __init__(self):
        super(PlrBaseSource, self).__init__()


class PlrDatabaseSource(PlrBaseSource):

    def __init__(self, adapter, model):
        """
        The plug for plrs which uses a database as source.
        :param adapter: The database adapter which provides access to the desired database session
        :type adapter: pyramid_oereb.lib.adapter.DatabaseAdapter
        :param model: The orm to map database source to plr style
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        """
        super(PlrDatabaseSource, self).__init__()
        self._adapter_ = adapter
        self._model_ = model

    def read(self, key):
        """
        Central method to read all plrs.
        :param key: Key of the desired database connection
        :type key: str
        """
        session = self._adapter_.get_session(key)
        results = session.query(self._model_).all()
        self.records = list()
        for r in results:
            d = dict()
            for f in PlrRecord.get_fields():
                d[f] = getattr(r, f)
            self.records.append(PlrRecord(**d))
