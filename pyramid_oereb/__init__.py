# -*- coding: utf-8 -*-

import logging

from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.config import ConfigReader, parse
from pyramid.config import Configurator

from pyramid_oereb.lib.readers.extract import ExtractReader
from pyramid_oereb.lib.readers.municipality import MunicipalityReader
from pyramid_oereb.lib.readers.real_estate import RealEstateReader
from pyramid_oereb.lib.processor import Processor

__version__ = '1.0.0-alpha.1'


log = logging.getLogger('pyramid_oereb')
route_prefix = None
config_reader = None
# initially instantiate database adapter for global session handling
database_adapter = DatabaseAdapter()
plr_cadastre_authority = None
real_estate_reader = None
municipality_reader = None
extract_reader = None
plr_sources = None
app_schema_name = None
srid = None


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. This is necessary for development of
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

    :param config: The pyramid apps config object
    :type config: Configurator
    """
    global route_prefix, config_reader, real_estate_reader, municipality_reader, extract_reader, \
        plr_sources, plr_cadastre_authority, app_schema_name, srid

    # Set route prefix
    route_prefix = config.route_prefix

    # Get settings
    settings = config.get_settings()

    # Load configuration file
    cfg_file = settings.get('pyramid_oereb.cfg.file', None)
    cfg_section = settings.get('pyramid_oereb.cfg.section', None)
    config_reader = ConfigReader(cfg_file, cfg_section)
    real_estate_config = config_reader.get_real_estate_config()
    municipality_config = config_reader.get_municipality_config()
    logos = config_reader.get_logo_config()
    app_schema_name = config_reader.get('app_schema').get('name')
    srid = config_reader.get('srid')

    plr_cadastre_authority = config_reader.get_plr_cadastre_authority()

    real_estate_reader = RealEstateReader(
        real_estate_config.get('source').get('class'),
        **real_estate_config.get('source').get('params')
    )

    municipality_reader = MunicipalityReader(
        municipality_config.get('source').get('class'),
        **municipality_config.get('source').get('params')
    )

    plr_sources = []
    for plr in config_reader.get('plrs'):
        plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
        plr_sources.append(plr_source_class(**plr))

    extract_reader = ExtractReader(
        plr_sources,
        plr_cadastre_authority,
        logos
    )

    settings.update({
        'pyramid_oereb': parse(cfg_file, cfg_section)
    })
    processor = Processor(
        real_estate_reader,
        municipality_reader,
        plr_sources,
        extract_reader
    )

    def pyramid_oereb_processor(request):
        return processor

    config.add_request_method(pyramid_oereb_processor, reify=True)

    config.include('pyramid_oereb.routes')
