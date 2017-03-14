# -*- coding: utf-8 -*-
import os
# from pyramid_georest import Api, Service

# from pyramid_oereb.models import RailwayConstructionLimits

__author__ = 'Clemens Rudert'
__create_date__ = '01.02.2017'

DB_URL = os.environ.get('SQLALCHEMY_URL', 'postgresql://www-data:www-data@localhost:5432/oereb_test')


def includeme(config):
    config.include('pyramid_georest')
#     create_test_api(config)
#
#
# def create_test_api(config):
#     test_api = Api(DB_URL, config, name='api')
#     test_service = Service(RailwayConstructionLimits)
#     test_api.add_service(test_service)
#     return test_api
