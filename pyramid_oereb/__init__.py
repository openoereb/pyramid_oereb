# -*- coding: utf-8 -*-

import logging

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.config import ConfigReader
from pyramid.config import Configurator

from pyramid_oereb.lib.config import parse
from pyramid_oereb.lib.readers.municipality import MunicipalityReader
from pyramid_oereb.lib.readers.real_estate import RealEstateReader

__version__ = '0.0.1'


log = logging.getLogger('pyramid_oereb')
route_prefix = None
config_reader = None
# initially instantiate database adapter for global session handling
database_adapter = DatabaseAdapter()
real_estate_reader = None
municipality_reader = None


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
    global route_prefix, config_reader, real_estate_reader, municipality_reader

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

    real_estate_reader = RealEstateReader(
        real_estate_config.get('source').get('class'),
        **real_estate_config.get('source').get('params')
    )

    municipality_reader = MunicipalityReader(
        municipality_config.get('source').get('class'),
        **municipality_config.get('source').get('params')
    )

    settings.update({
        'pyramid_oereb': parse(cfg_file, cfg_section)
    })

    config.include('pyramid_oereb.routes')


# TODO: remove this method when approach is more clear
def _test_flow():
    global config_reader
    from pyramid_oereb.lib.sources.real_estate import RealEstateDatabaseSource
    from pyramid_oereb.lib.sources.extract import ExtractStandardDatabaseSource
    config_reader = ConfigReader('pyramid_oereb.yml', 'pyramid_oereb')
    re_dbs = RealEstateDatabaseSource(
        **{'db_connection': 'postgresql://postgres:password@localhost/pyramid_oereb',
           'model': 'pyramid_oereb.models.PyramidOerebMainRealEstate'})
    re_dbs.read(egrid='CH113928077734')
    extract = ExtractStandardDatabaseSource(
        **{'db_connection': 'postgresql://postgres:password@localhost/pyramid_oereb',
           'name': 'plr119'})
    extract.read(re_dbs.records[0])
    return extract
