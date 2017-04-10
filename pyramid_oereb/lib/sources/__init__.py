# -*- coding: utf-8 -*-
from pyramid.config import ConfigurationError


class Base(object):
    records = list()


class BaseDatabaseSource(Base):

    def __init__(self, key, model):
        from pyramid_oereb import database_adapter
        """
        The plug for sources which uses a database.
        :param key: The key for the database connection which should be used from the database adapter,
        passed to this instance.
        :type key: str
        :param adapter: The database adapter which provides access to the desired database session
        :type adapter: pyramid_oereb.lib.adapter.DatabaseAdapter
        :param model: The orm to map database source to plr style
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        """
        if database_adapter:
            self._adapter_ = database_adapter
        else:
            raise ConfigurationError('Adapter for database must be defined if you use database sources.')
        self._key_ = key
        self._model_ = model
