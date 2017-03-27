# -*- coding: utf-8 -*-

from pyramid_oereb import route_prefix
from pyramid_oereb.views.webservice import PlrWebservice

__author__ = 'Clemens Rudert'
__create_date__ = '01.02.2017'


def includeme(config):

    # Get versions
    config.add_route('{0}/versions.json'.format(route_prefix), '/versions.json')
    config.add_view(
        PlrWebservice,
        attr='get_versions',
        route_name='{0}/versions.json'.format(route_prefix),
        request_method='GET',
        renderer='json'
    )

    # Get capabilities
    config.add_route('{0}/capabilities.json'.format(route_prefix), '/capabilities.json')
    config.add_view(
        PlrWebservice,
        attr='get_capabilities',
        route_name='{0}/capabilities.json'.format(route_prefix),
        request_method='GET',
        renderer='json'
    )

    # Commit config
    config.commit()
