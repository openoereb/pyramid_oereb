# -*- coding: utf-8 -*-

import logging
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationConflictError

__author__ = 'Clemens Rudert'
__create_date__ = '01.02.2017'

log = logging.getLogger('pyramid_oereb')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. This is necessary for development of
    your plugin. So you can run it local with the paster server and in a IDE like PyCharm. It
    is intended to leave this section as is and do configuration in the includeme section only.
    Push additional configuration in this section means it will not be used by the production
    environment at all!
    """
    config = Configurator(settings=settings)
    config.include('pyramid_oereb', route_prefix='api')
    config.scan()
    return config.make_wsgi_app()


def includeme(config):
    """
    By including this in your pyramid web app you can easily provide a running OEREB Server

    :param config: The pyramid apps config object
    :type config: Configurator
    """

    # bind the mako renderer to other file extensions
    try:
        add_mako_renderer(config, ".html")
        config.commit()
    except ConfigurationConflictError as e:
        log.debug('Renderer for "html" already exists: {0}'.format(e.message))
    try:
        add_mako_renderer(config, ".js")
        config.commit()
    except ConfigurationConflictError as e:
        log.debug('Renderer for "js" already exists: {0}'.format(e.message))

    includeme('pyramid_oereb.routes')
