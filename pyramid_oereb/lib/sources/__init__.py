# -*- coding: utf-8 -*-
from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver


class Base(object):
    records = list()


class BaseDatabaseSource(Base):

    def __init__(self, **kwargs):
        from pyramid_oereb import database_adapter
        """
        The plug for addresses which uses a database as source.

        Args:
            kwargs (dict): Arbitrary keyword arguments. It must contain the keys 'db_connection'
                and 'model'.The db_connection value must be a rfc1738 conform database
                connection string in the form of:'<driver_name e.g. "
                postgres">://<username>:<password>@<database_host>:<port>/<database_na
                me>'The model must be a valid dotted name string which leads to an
                importable representation of:sqlalchemy.ext.declarative.DeclarativeMeta or
                the real class itself.
        """
        if database_adapter:
            self._adapter_ = database_adapter
        else:
            raise ConfigurationError('Adapter for database must be defined if you use database sources.')
        if kwargs.get('db_connection'):
            self._key_ = kwargs.get('db_connection')
        else:
            raise ConfigurationError('"db_connection" for source has to be defined in used yaml '
                                     'configuration file')
        if kwargs.get('model'):
            self._model_ = DottedNameResolver().maybe_resolve(kwargs.get('model'))
        else:
            raise ConfigurationError('"model" for source has to be defined in used yaml configuration file')
