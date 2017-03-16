# -*- coding: utf-8 -*-
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


log = logging.getLogger('pyramid_oereb')


class DatabaseAdapter(object):
    _connections_ = dict()

    def __init__(self):
        pass

    def add_connection(self, connection_string):
        if connection_string not in self._connections_:
            engine = create_engine(connection_string)
            session = sessionmaker(bind=engine)
            self._connections_[connection_string] = {
                'engine': engine,
                'session': session
            }
        else:
            log.info('Connection already exists: {0}'.format(connection_string))

    def get_session(self, key, request=None):
        if key in self._connections_:
            session = self._connections_.get(key).get('session')
            return session()
        else:
            raise KeyError('No connection found: {0}'.format(key))