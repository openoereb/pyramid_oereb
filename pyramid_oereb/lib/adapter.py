# -*- coding: utf-8 -*-
import logging
from sqlalchemy import create_engine, orm
from sqlalchemy.orm import sessionmaker


log = logging.getLogger('pyramid_oereb')


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
        :param connection_string: The rfc1738 URL string which defines the database connection
        :type connection_string: str
        """
        if connection_string not in self._connections_:
            engine = create_engine(connection_string)
            session = orm.scoped_session(sessionmaker(bind=engine, autocommit=True))
            self._connections_[connection_string] = {
                'engine': engine,
                'session': session
            }
        else:
            log.info('Connection already exists: {0}'.format(connection_string))

    def get_connections(self):
        """
        Returns a dictionary with the available connections.
        :return: The available connections.
        :rtype: dict
        """
        return self._connections_

    def get_session(self, key, request=None):
        """
        The point where you will get what you need: The session to talk to the database!
        :param key: The key to identify the desired connection in the pool of available connections.
        :type key: str
        :param request: The request of the underlying pyramid application. This can be useful to handle error
        cases and treat sessions in the right way.
        :type request: pyramid.request.Request or None
        :return: The requested clean session instance ready for use
        :rtype: sqlalchemy.orm.Session
        :raises: KeyError
        """
        if key in self._connections_:
            session = self._connections_.get(key).get('session')
            return session()
        else:
            self.add_connection(key)
            log.info('Connection does not exist, implicitly creating it: {0}'.format(key))
            return self.get_session(key, request=request)
