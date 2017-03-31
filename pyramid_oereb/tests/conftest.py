# -*- coding: utf-8 -*-

from pyramid_oereb.lib.config import parse, ConfigReader

db_url = parse('pyramid_oereb_test.yml', 'pyramid_oereb').get('db_connection')
config_reader = ConfigReader('pyramid_oereb_test.yml', 'pyramid_oereb')
