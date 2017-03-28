# -*- coding: utf-8 -*-

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.config import parse

db_url = parse('pyramid_oereb_test.yml', 'pyramid_oereb').get('db_connection')
adapter = DatabaseAdapter()
