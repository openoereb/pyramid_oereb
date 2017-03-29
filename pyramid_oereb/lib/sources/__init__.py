# -*- coding: utf-8 -*-


class Base(object):
    records = list()


class BaseDatabaseSource(Base):

    def __init__(self, key, adapter, model, record_class):
        """
        The plug for properties which uses a database as source.
        :param key: The key for the database connection which should be used from the database adapter,
        passed to this instance.
        :type key: str
        :param adapter: The database adapter which provides access to the desired database session
        :type adapter: pyramid_oereb.lib.adapter.DatabaseAdapter
        :param model: The orm to map database source to plr style
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        :param record_class: The class of the record which is used for mapping inside of the application
        :type record_class: pyramid_oereb.lib.records.BaseRecord
        """
        self._adapter_ = adapter
        self._key_ = key
        self._model_ = model
        self._record_class_ = record_class
