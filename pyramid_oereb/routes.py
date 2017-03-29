# -*- coding: utf-8 -*-

from pyramid_oereb import route_prefix
from pyramid_oereb.views.webservice import PlrWebservice


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
    config.add_route('{0}/versions'.format(route_prefix), '/versions')
    config.add_view(
        PlrWebservice,
        attr='get_versions',
        route_name='{0}/versions'.format(route_prefix),
        request_method='GET',
        renderer='json'  # TODO: Replace by XML renderer
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
    config.add_route('{0}/capabilities'.format(route_prefix), '/capabilities')
    config.add_view(
        PlrWebservice,
        attr='get_capabilities',
        route_name='{0}/capabilities'.format(route_prefix),
        request_method='GET',
        renderer='json'  # TODO: Replace by XML renderer
    )

    # Get egrid
    config.add_route('{0}/getegrid_coord'.format(route_prefix), '/getegrid')
    config.add_route('{0}/getegrid_ident'.format(route_prefix), '/getegrid/{identdn}/{number}')
    config.add_route('{0}/getegrid_address'.format(route_prefix),
                     '/getegrid/{postalcode}/{localisation}/{number}')
    config.add_view(
        PlrWebservice,
        attr='get_egrid_coord',
        route_name='{0}/getegrid_coord'.format(route_prefix),
        request_method='GET',
        renderer='json'  # TODO: Replace by XML renderer
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_ident',
        route_name='{0}/getegrid_ident'.format(route_prefix),
        request_method='GET',
        renderer='json'  # TODO: Replace by XML renderer
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_address',
        route_name='{0}/getegrid_address'.format(route_prefix),
        request_method='GET',
        renderer='json'  # TODO: Replace by XML renderer
    )

    # Commit config
    config.commit()
