# -*- coding: utf-8 -*-

import logging

from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.config import Config, parse
from pyramid.config import Configurator

from pyramid_oereb.lib.readers.exclusion_of_liability import ExclusionOfLiabilityReader
from pyramid_oereb.lib.readers.extract import ExtractReader
from pyramid_oereb.lib.readers.glossary import GlossaryReader
from pyramid_oereb.lib.readers.municipality import MunicipalityReader
from pyramid_oereb.lib.readers.real_estate import RealEstateReader
from pyramid_oereb.lib.processor import Processor

__version__ = '1.0.1'


log = logging.getLogger(__name__)
route_prefix = None
# initially instantiate database adapter for global session handling
database_adapter = DatabaseAdapter()
app_schema_name = None
srid = None


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

    global route_prefix, app_schema_name, srid

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

    real_estate_config = Config.get_real_estate_config()
    municipality_config = Config.get_municipality_config()
    exclusion_of_liability_config = Config.get_exclusion_of_liability_config()
    glossary_config = Config.get_glossary_config()
    extract = Config.get_extract_config()
    certification = extract.get('certification')
    certification_at_web = extract.get('certification_at_web')
    logos = Config.get_logo_config()
    app_schema_name = Config.get('app_schema').get('name')
    srid = Config.get('srid')

    plr_cadastre_authority = Config.get_plr_cadastre_authority()

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
    for plr in Config.get('plrs'):
        plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
        plr_sources.append(plr_source_class(**plr))

    extract_reader = ExtractReader(
        plr_sources,
        plr_cadastre_authority,
        logos,
        certification,
        certification_at_web,
    )

    settings.update({
        'pyramid_oereb': parse(cfg_file or cfg_c2ctemplate_file, cfg_section, cfg_file is None)
    })
    processor = Processor(
        real_estate_reader=real_estate_reader,
        municipality_reader=municipality_reader,
        exclusion_of_liability_reader=exclusion_of_liability_reader,
        glossary_reader=glossary_reader,
        plr_sources=plr_sources,
        extract_reader=extract_reader,
    )

    def pyramid_oereb_processor(request):
        return processor

    config.add_request_method(pyramid_oereb_processor, reify=True)

    config.add_renderer('pyramid_oereb_extract_json', 'pyramid_oereb.lib.renderer.extract.json_.Renderer')
    config.add_renderer('pyramid_oereb_extract_xml', 'pyramid_oereb.lib.renderer.extract.xml_.Renderer')
    config.add_renderer('pyramid_oereb_extract_print', Config.get('print').get('renderer'))
    config.add_renderer('pyramid_oereb_versions_xml', 'pyramid_oereb.lib.renderer.versions.xml_.Renderer')
    config.add_renderer('pyramid_oereb_capabilities_xml',
                        'pyramid_oereb.lib.renderer.capabilities.xml_.Renderer')
    config.add_renderer('pyramid_oereb_getegrid_xml', 'pyramid_oereb.lib.renderer.getegrid.xml_.Renderer')

    config.include('pyramid_oereb.routes')
