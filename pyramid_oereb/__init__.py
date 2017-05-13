# -*- coding: utf-8 -*-

import logging

from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.config import ConfigReader, parse
from pyramid.config import Configurator

from pyramid_oereb.lib.readers.exclusion_of_liability import ExclusionOfLiabilityReader
from pyramid_oereb.lib.readers.extract import ExtractReader
from pyramid_oereb.lib.readers.glossary import GlossaryReader
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
plr_limits = None
app_schema_name = None
srid = None
default_lang = None


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

    :param config: The pyramid apps config object
    :type config: Configurator
    """
    global route_prefix, config_reader, real_estate_reader, municipality_reader,  extract_reader, \
        plr_sources, plr_cadastre_authority, app_schema_name, srid, default_lang

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
    exclusion_of_liability_config = config_reader.get_exclusion_of_liability_config()
    glossary_config = config_reader.get_glossary_config()
    logos = config_reader.get_logo_config()
    app_schema_name = config_reader.get('app_schema').get('name')
    srid = config_reader.get('srid')
    point_types = config_reader.get('plr_limits').get('point_types')
    line_types = config_reader.get('plr_limits').get('line_types')
    polygon_types = config_reader.get('plr_limits').get('polygon_types')
    min_length = config_reader.get('plr_limits').get('min_length')
    min_area = config_reader.get('plr_limits').get('min_area')
    default_lang = config_reader.get('default_language')

    plr_cadastre_authority = config_reader.get_plr_cadastre_authority()

    real_estate_reader = RealEstateReader(
        real_estate_config.get('source').get('class'),
        **real_estate_config.get('source').get('params')
    )

    municipality_reader = MunicipalityReader(
        municipality_config.get('source').get('class'),
        **municipality_config.get('source').get('params')
    )

    exclusion_of_liability_reader = ExclusionOfLiabilityReader(
        exclusion_of_liability_config.get('source').get('class'),
        **exclusion_of_liability_config.get('source').get('params')
    )

    glossary_reader = GlossaryReader(
        glossary_config.get('source').get('class'),
        **glossary_config.get('source').get('params')
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
        real_estate_reader=real_estate_reader,
        municipality_reader=municipality_reader,
        exclusion_of_liability_reader=exclusion_of_liability_reader,
        glossary_reader=glossary_reader,
        plr_sources=plr_sources,
        extract_reader=extract_reader,
        point_types=point_types,
        line_types=line_types,
        polygon_types=polygon_types,
        min_length=min_length,
        min_area=min_area
    )

    def pyramid_oereb_processor(request):
        return processor

    def pyramid_oereb_config_reader(request):
        return config_reader

    config.add_request_method(pyramid_oereb_processor, reify=True)
    config.add_request_method(pyramid_oereb_config_reader, reify=True)

    config.add_renderer('pyramid_oereb_extract_json', 'pyramid_oereb.lib.renderer._json_.Extract')
    config.add_renderer('pyramid_oereb_extract_xml', 'pyramid_oereb.lib.renderer._xml_.Extract')

    config.include('pyramid_oereb.routes')
