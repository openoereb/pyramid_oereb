# -*- coding: utf-8 -*-
from pyramid_oereb import route_prefix
from pyramid_oereb.core.views.webservice import PlrWebservice, Symbol, Logo, Sld
from pyramid_oereb.contrib.stats.decorators import log_response


def includeme(config):  # pragma: no cover
    """
    Create all necessary routes and views for the `pyramid_oereb` application.

    Args:
        config (pyramid.config.Configurator): The application's configurator instance.
    """

    # Service for logo images
    config.add_route('{0}/image/logo'.format(route_prefix),
                     '/image/logo/{logo}/{language}.{extension}')
    config.add_view(Logo, attr='get_image', route_name='{0}/image/logo'.format(route_prefix),
                    request_method='GET',
                    decorator=log_response)

    # Service for symbol images
    config.add_route('{0}/image/symbol'.format(route_prefix),
                     '/image/symbol/{theme_code}/legend_entry.{extension}')

    config.add_view(Symbol, attr='get_image', route_name='{0}/image/symbol'.format(route_prefix),
                    request_method='GET',
                    decorator=log_response)

    # Service for sld creation on egrid input
    config.add_route('{0}/sld'.format(route_prefix), '/sld')
    config.add_view(Sld, attr='get_sld', route_name='{0}/sld'.format(route_prefix),
                    request_method='GET',
                    decorator=log_response)

    # Get versions
    config.add_route('{0}/versions'.format(route_prefix), '/versions/{format}')
    config.add_view(
        PlrWebservice,
        attr='get_versions',
        route_name='{0}/versions'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )
    config.add_route('{0}/versions/'.format(route_prefix), '/versions/{format}/')
    config.add_view(
        PlrWebservice,
        attr='get_versions',
        route_name='{0}/versions/'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )

    # Get capabilities
    config.add_route('{0}/capabilities'.format(route_prefix), '/capabilities/{format}')
    config.add_view(
        PlrWebservice,
        attr='get_capabilities',
        route_name='{0}/capabilities'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )
    config.add_route('{0}/capabilities/'.format(route_prefix), '/capabilities/{format}/')
    config.add_view(
        PlrWebservice,
        attr='get_capabilities',
        route_name='{0}/capabilities/'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )

    # Get egrid
    config.add_route('{0}/getegrid'.format(route_prefix),
                     '/getegrid/{format}')
    config.add_view(
        PlrWebservice,
        attr='get_egrid',
        route_name='{0}/getegrid'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )
    config.add_route('{0}/getegrid/'.format(route_prefix),
                     '/getegrid/{format}/')
    config.add_view(
        PlrWebservice,
        attr='get_egrid',
        route_name='{0}/getegrid/'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )

    # Get extract by id
    config.add_route('{0}/extract'.format(route_prefix),
                     '/extract/{format}')
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )
    config.add_route('{0}/extract/'.format(route_prefix),
                     '/extract/{format}/')
    config.add_view(
        PlrWebservice,
        attr='get_extract_by_id',
        route_name='{0}/extract/'.format(route_prefix),
        request_method='GET',
        decorator=log_response
    )

    # Commit config
    config.commit()
