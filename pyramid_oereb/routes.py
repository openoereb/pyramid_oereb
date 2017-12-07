# -*- coding: utf-8 -*-
from pyramid_oereb import route_prefix
from pyramid_oereb.views.webservice import PlrWebservice, Symbol, Logo, Municipality, Sld


def includeme(config):  # pragma: no cover
    """
    Create all necessary routes and views for the `pyramid_oereb` application.

    Args:
        config (pyramid.config.Configurator): The application's configurator instance.
    """

    # Service for logo images
    config.add_route('{0}/image/logo'.format(route_prefix), '/image/logo/{logo}')
    config.add_view(Logo, attr='get_image', route_name='{0}/image/logo'.format(route_prefix),
                    request_method='GET')

    # Service for municipality images
    config.add_route('{0}/image/municipality'.format(route_prefix), '/image/municipality/{fosnr}')
    config.add_view(Municipality, attr='get_image', route_name='{0}/image/municipality'.format(route_prefix),
                    request_method='GET')

    # Service for symbol images
    config.add_route('{0}/image/symbol'.format(route_prefix),
                     '/image/symbol/{theme_code}/{type_code}')
    config.add_view(Symbol, attr='get_image', route_name='{0}/image/symbol'.format(route_prefix),
                    request_method='GET')

    # Service for sld creation on egrid input
    config.add_route('{0}/sld'.format(route_prefix), '/sld')
    config.add_view(Sld, attr='get_sld', route_name='{0}/sld'.format(route_prefix),
                    request_method='GET')

    # Get versions
    config.add_route('{0}/versions.json'.format(route_prefix), '/versions.json')
    config.add_view(
        PlrWebservice,
        attr='get_versions',
        route_name='{0}/versions.json'.format(route_prefix),
        request_method='GET'
    )
    config.add_route('{0}/versions'.format(route_prefix), '/versions')
    config.add_view(
        PlrWebservice,
        attr='get_versions',
        route_name='{0}/versions'.format(route_prefix),
        request_method='GET'
    )
    config.add_route('{0}/versions/'.format(route_prefix), '/versions/')
    config.add_view(
        PlrWebservice,
        attr='get_versions',
        route_name='{0}/versions/'.format(route_prefix),
        request_method='GET'
    )

    # Get capabilities
    config.add_route('{0}/capabilities.json'.format(route_prefix), '/capabilities.json')
    config.add_view(
        PlrWebservice,
        attr='get_capabilities',
        route_name='{0}/capabilities.json'.format(route_prefix),
        request_method='GET'
    )
    config.add_route('{0}/capabilities'.format(route_prefix), '/capabilities')
    config.add_view(
        PlrWebservice,
        attr='get_capabilities',
        route_name='{0}/capabilities'.format(route_prefix),
        request_method='GET'
    )
    config.add_route('{0}/capabilities/'.format(route_prefix), '/capabilities/')
    config.add_view(
        PlrWebservice,
        attr='get_capabilities',
        route_name='{0}/capabilities/'.format(route_prefix),
        request_method='GET'
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
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_ident',
        route_name='{0}/getegrid_ident.json'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_address',
        route_name='{0}/getegrid_address.json'.format(route_prefix),
        request_method='GET'
    )
    config.add_route('{0}/getegrid_coord'.format(route_prefix), '/getegrid')
    config.add_route('{0}/getegrid_ident'.format(route_prefix), '/getegrid/{identdn}/{number}')
    config.add_route('{0}/getegrid_address'.format(route_prefix),
                     '/getegrid/{postalcode}/{localisation}/{number}')
    config.add_view(
        PlrWebservice,
        attr='get_egrid_coord',
        route_name='{0}/getegrid_coord'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_ident',
        route_name='{0}/getegrid_ident'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_address',
        route_name='{0}/getegrid_address'.format(route_prefix),
        request_method='GET'
    )
    config.add_route('{0}/getegrid_coord/'.format(route_prefix), '/getegrid/')
    config.add_route('{0}/getegrid_ident/'.format(route_prefix), '/getegrid/{identdn}/{number}/')
    config.add_route('{0}/getegrid_address/'.format(route_prefix),
                     '/getegrid/{postalcode}/{localisation}/{number}/')
    config.add_view(
        PlrWebservice,
        attr='get_egrid_coord',
        route_name='{0}/getegrid_coord/'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_ident',
        route_name='{0}/getegrid_ident/'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_egrid_address',
        route_name='{0}/getegrid_address/'.format(route_prefix),
        request_method='GET'
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
    config.add_route('{0}/extract_1/'.format(route_prefix),
                     '/extract/{flavour}/{format}/{param1}/')
    config.add_route('{0}/extract_2/'.format(route_prefix),
                     '/extract/{flavour}/{format}/{param1}/{param2}/')
    config.add_route('{0}/extract_3/'.format(route_prefix),
                     '/extract/{flavour}/{format}/{param1}/{param2}/{param3}/')
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract_1/'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract_2/'.format(route_prefix),
        request_method='GET'
    )
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract_3/'.format(route_prefix),
        request_method='GET'
    )

    # Commit config
    config.commit()
