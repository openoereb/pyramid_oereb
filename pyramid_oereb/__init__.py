# -*- coding: utf-8 -*-

import logging

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.config import Config
from pyramid.config import Configurator

__version__ = '1.0.1'


log = logging.getLogger(__name__)
route_prefix = None
# initially instantiate database adapter for global session handling
database_adapter = DatabaseAdapter()


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application. This is necessary for development of
    your plugin. So you can run it local with the paster server and in a IDE like PyCharm. It
    is intended to leave this section as is and do configuration in the includeme section only.
    Push additional configuration in this section means it will not be used by the production
    environment at all!
    """
    config = Configurator(settings=settings)
    config.include('pyramid_oereb', route_prefix='oereb')
    config.scan()
    return config.make_wsgi_app()


def includeme(config):
    """
    By including this in your pyramid web app you can easily provide a running OEREB Server

    Args:
        config (Configurator): The pyramid apps config object
    """

    global route_prefix

    # Set route prefix
    route_prefix = config.route_prefix

    # Get settings
    settings = config.get_settings()

    # Load configuration file
    cfg_file = settings.get('pyramid_oereb.cfg.file', None)
    cfg_c2ctemplate_file = settings.get('pyramid_oereb.cfg.c2ctemplate.file', None)
    cfg_section = settings.get('pyramid_oereb.cfg.section', None)
    Config.init(cfg_file or cfg_c2ctemplate_file, cfg_section, cfg_file is None)
    Config.update_settings(settings)

    settings.update({
        'pyramid_oereb': Config.get_config()
    })

    config.add_renderer('pyramid_oereb_extract_json', 'pyramid_oereb.lib.renderer.extract.json_.Renderer')
    config.add_renderer('pyramid_oereb_extract_xml', 'pyramid_oereb.lib.renderer.extract.xml_.Renderer')
    config.add_renderer('pyramid_oereb_extract_print', Config.get('print').get('renderer'))
    config.add_renderer('pyramid_oereb_versions_xml', 'pyramid_oereb.lib.renderer.versions.xml_.Renderer')
    config.add_renderer('pyramid_oereb_capabilities_xml',
                        'pyramid_oereb.lib.renderer.capabilities.xml_.Renderer')
    config.add_renderer('pyramid_oereb_getegrid_xml', 'pyramid_oereb.lib.renderer.getegrid.xml_.Renderer')

    config.include('pyramid_oereb.routes')
