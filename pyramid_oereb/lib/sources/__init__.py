# -*- coding: utf-8 -*-
"""
This is package provides the minimum requirements on the classes which can be used as a source.
"""
from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver


class Base(object):
    """
    The basic source class. This is not meant to be used directly as a source at runtime. But more as a basic
    class for inherit in special designed classes.

    Attributes:
        records (list): The list which will be filled up with records in the process.
    """
    records = list()


class BaseDatabaseSource(Base):
    """
    The plug for addresses which uses a database as source.
    """

    def __init__(self, **kwargs):
        """

        Keyword Args:
            db_connection (str): A rfc1738 conform database connection string in the form of:
                ``<driver_name>://<username>:<password>@<database_host>:<port>/<database_name>``
            model (str): A valid dotted name string which leads to an importable representation of
                sqlalchemy.ext.declarative.DeclarativeMeta or the real class itself.
        """
        from pyramid_oereb import database_adapter

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
