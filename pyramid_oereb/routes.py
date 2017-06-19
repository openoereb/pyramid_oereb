# -*- coding: utf-8 -*-

from pyramid_oereb import route_prefix
from pyramid_oereb.views.webservice import PlrWebservice


def includeme(config):  # pragma: no cover

    # Static view for images
    config.add_static_view('images', '/tmp/test')

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
        renderer='pyramid_oereb_versions_xml'
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
        renderer='pyramid_oereb_capabilities_xml'
    )

    # Get egrid
    config.add_route('{0}/getegrid_coord.json'.format(route_prefix), '/getegrid.json')
    config.add_route('{0}/getegrid_ident.json'.format(route_prefix), '/getegrid/{identdn}/{number}.json')
    config.add_route('{0}/getegrid_address.json'.format(route_prefix),
                     '/getegrid/{postalcode}/{localisation}/{number}.json')
    config.add_view(
        PlrWebservice,
        attr='get_egrid_coord',
        route_name='{0}/getegrid_coord.json'.format(route_prefix),
        request_method='GET',
        renderer='json'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_ident',
        route_name='{0}/getegrid_ident.json'.format(route_prefix),
        request_method='GET',
        renderer='json'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_address',
        route_name='{0}/getegrid_address.json'.format(route_prefix),
        request_method='GET',
        renderer='json'
    )
    config.add_route('{0}/getegrid_coord'.format(route_prefix), '/getegrid')
    config.add_route('{0}/getegrid_ident'.format(route_prefix), '/getegrid/{identdn}/{number}')
    config.add_route('{0}/getegrid_address'.format(route_prefix),
                     '/getegrid/{postalcode}/{localisation}/{number}')
    config.add_view(
        PlrWebservice,
        attr='get_egrid_coord',
        route_name='{0}/getegrid_coord'.format(route_prefix),
        request_method='GET',
        renderer='pyramid_oereb_getegrid_xml'  # TODO: Replace by XML renderer
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_ident',
        route_name='{0}/getegrid_ident'.format(route_prefix),
        request_method='GET',
        renderer='pyramid_oereb_getegrid_xml'  # TODO: Replace by XML renderer
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_address',
        route_name='{0}/getegrid_address'.format(route_prefix),
        request_method='GET',
        renderer='pyramid_oereb_getegrid_xml'  # TODO: Replace by XML renderer
    )

    # Get extract by id
    config.add_route('{0}/extract_1'.format(route_prefix),
                     '/extract/{flavour}/{format}/{param1}')
    config.add_route('{0}/extract_2'.format(route_prefix),
                     '/extract/{flavour}/{format}/{param1}/{param2}')
    config.add_route('{0}/extract_3'.format(route_prefix),
                     '/extract/{flavour}/{format}/{param1}/{param2}/{param3}')
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract_1'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract_2'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract_3'.format(route_prefix),
        request_method='GET'
    )

    # Commit config
    config.commit()
