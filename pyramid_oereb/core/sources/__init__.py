# -*- coding: utf-8 -*-
"""
This is package provides the minimum requirements on the classes which can be used as a source.
"""
import time
import logging
from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver

log = logging.getLogger(__name__)


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

    Attributes:
        TIMEOUT (int): Seconds to wait until database should be ready
    """

    TIMEOUT = 60

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
        # check if database is available and wait until it might be or raise error
        timeout_target = time.time() + self.TIMEOUT
        db_healthy = False
        current_wait_position = 0
        sleep_period = 1.0
        while time.time() < timeout_target:
            db_healthy = self.health_check()
            if not db_healthy:
                current_wait_position += int(sleep_period)
                # 1.0 sets it to a second
                log.info('Waiting for the database {} more seconds ({})'.format(
                    self.TIMEOUT - current_wait_position,
                    self._key_
                ))
                time.sleep(sleep_period)
            else:
                break
        if not db_healthy:
            raise ConfigurationError('Database was not reached until timeout of {} seconds ({})'.format(
                self.TIMEOUT,
                self._key_
            ))

    def get_session(self):
        return self._adapter_.get_session(self._key_)

    def health_check(self):
        session = self._adapter_.get_session(self._key_)
        try:
            session.execute('SELECT 1')
            return True
        except Exception:
            return False
