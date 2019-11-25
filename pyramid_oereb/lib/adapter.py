# -*- coding: utf-8 -*-
import logging
import os

from io import open
from sqlalchemy import create_engine, orm


log = logging.getLogger(__name__)


class DatabaseAdapter(object):
    _connections_ = dict()

    def __init__(self):
        """
        This Class provides a bucket for database connection handling. It uses SQLalchemy for database talk.
        It enables distinct session sharing on the rfc1738 URL string. This reduces the amount of used
        sessions drastically.
        """
        pass

    def add_connection(self, connection_string):
        """
        Adds a new connection to this object. Also creates the necessary engine and session object.

        Args:
            connection_string (str): The rfc1738 URL string which defines the database
                connection
        """
        if connection_string not in self._connections_:
            engine = create_engine(connection_string, pool_recycle=30)
            session = orm.scoped_session(orm.sessionmaker(bind=engine))
            self._connections_[connection_string] = {
                'engine': engine,
                'session': session
            }
        else:
            log.info('Connection already exists: {0}'.format(connection_string))

    def get_connections(self):
        """
        Returns a dictionary with the available connections.

        Returns:
            dict: The available connections.
        """
        return self._connections_

    def get_session(self, key, request=None):
        """
        The point where you will get what you need: The session to talk to the database!

        Args:
            key (str): The key to identify the desired connection in the pool of available
                connections.
            request (pyramid.request.Request or None): The request of the underlying pyramid
                application. This can be useful to handle errorcases and treat sessions in
                the right way.

        Returns:
            sqlalchemy.orm.Session: The requested clean session instance ready for use

        Raises:
            KeyError
        """
        if key in self._connections_:
            session = self._connections_.get(key).get('session')
            return session()
        else:
            self.add_connection(key)
            log.info('Connection does not exist, implicitly creating it: {0}'.format(key))
            return self.get_session(key, request=request)


class FileAdapter(object):

    def __init__(self, cwd=None):
        self._cwd_ = os.path.abspath(cwd or '.')

    @property
    def cwd(self):
        return self._cwd_

    def cd(self, path):
        self._cwd_ = os.path.abspath(os.path.join(self._cwd_, path))

    def ls(self):
        result = list()
        for entry in os.listdir(self._cwd_):
            path = os.path.join(self._cwd_, entry)
            result.append((entry, {
                'is_file': os.path.isfile(path),
                'is_dir': os.path.isdir(path),
                'modified': os.path.getmtime(path)
            }))
        return result

    def read(self, filename, mode='rb'):
        filepath = os.path.join(self._cwd_, filename)
        if os.path.isfile(filepath):
            with open(filepath, mode=mode) as f:
                content = f.read()
            return content
        else:
            raise IOError('Not a file: {0}'.format(filepath))
