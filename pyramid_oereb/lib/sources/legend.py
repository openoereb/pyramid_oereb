# -*- coding: utf-8 -*-
from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.records.view_service import LegendEntryRecord


class LegendDatabaseSource(BaseDatabaseSource):

    def __init__(self, **kwargs):
        """
        The plug for the legend which uses a database as source.
        :param kwargs: Arbitrary keyword arguments. It must contain the keys 'db_connection' and 'model'
        """
        if kwargs.get('db_connection'):
            key = kwargs.get('db_connection')
        else:
            raise ConfigurationError('"db_connection" for source has to be defined in used yaml '
                                     'configuration file')
        if kwargs.get('model'):
            model = DottedNameResolver().resolve(kwargs.get('model'))
        else:
            raise ConfigurationError('"model" for source has to be defined in used yaml configuration file')

        super(LegendDatabaseSource, self).__init__(key, model)

    def read(self, **kwargs):
        """
        Central method to read one legend entry.
        :param kwargs: Arbitrary keyword arguments. It must contain the keys 'symbol', 'legend_text',
        'type_code', 'type_code_list' and 'theme'.
        """
        session = self._adapter_.get_session(self._key_)
        query = session.query(self._model_)
        if kwargs.get('symbol') and kwargs.get('legend_text') and kwargs.get('type_code') \
                and kwargs.get('type_code_list') and kwargs.get('theme'):
            results = [query.filter(
                self._model_.symbol == kwargs.get('symbol')
            ).filter(
                self._model_.legend_text == kwargs.get('legend_text')
            ).filter(
                self._model_.type_code == kwargs.get('type_code')
            ).filter(
                self._model_.type_code_list == kwargs.get('type_code_list')
            ).filter(
                self._model_.theme == kwargs.get('theme')
            ).one()]
        else:
            raise AttributeError('Necessary parameter were missing.')

        self.records = list()
        for result in results:
            self.records.append(LegendEntryRecord(
                result.symbol,
                result.legend_text,
                result.type_code,
                result.type_code_list,
                result.theme
            ))
