# -*- coding: utf-8 -*-
from pyramid.config import ConfigurationError


class Base(object):
    records = list()

    def read(self, geometry):
        """
        Every source class has to implement a read method. This is the point to hook in for adapt core system
        to the defined source. Here you can do what ever is necessary to map a entity read from your source
        to the corresponding core system record.
        :param geometry: The geometry as WKT string which represents the desired property. It can be used for
        intersection operations.
        :type geometry: str
        """
        raise ConfigurationError('The read method must be adapted to your system. ')


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
