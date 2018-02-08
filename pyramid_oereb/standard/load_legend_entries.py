# -*- coding: utf-8 -*-

import sys
import optparse
import logging

from pyconizer import create_icons_from_scratch, get_icon
from pyconizer.lib.url import parse_url
from pyramid.path import DottedNameResolver
from sqlalchemy import create_engine, orm

from pyramid_oereb import parse

if sys.version_info.major == 2:
    from urlparse import urlunsplit
else:

    from urllib.parse import urlunsplit


logging.basicConfig()
log = logging.getLogger(__name__)


def create_legend_entries_in_standard_db(config, topic_code, temp_creation_path='/tmp/pyconizer',
                                         language='de', section='pyramid_oereb', image_format='image/png',
                                         image_height=36, image_width=72, encoding=None, replace_host=None,
                                         replace_layer=None, string_keys=False, by_type_code=False):
    """
    Uses the pyconizer lib to create images out of the OEREB server configuration. It is creating symbols for
    a dedicated topic. This function will clean all previously created icons from database.

    Args:
        config (str): The path to the used OEREB server configuration YAML file.
        topic_code (str): The topic code for which the symbols should be created. It must be configured in
            the passed yml.
        temp_creation_path: The path where the images are created in.
        language: The language which is used to produce the WMS rules. This is a tricky part. You must
            provide the language your WMS is using.
        section: The section which the config can be found in the yml.
        image_format: The image format. This is passed throug to the WMS request. You need to provide a
            format your WMS is supporting here.
        image_height: The height of the produced image.
        image_width: The width of the produced image.
        encoding (str or unicode): The encoding which is used to encode the XML. Standard is None. This means
            the encoding is taken from the XML content itself. Only use this parameter if your XML content
            has no encoding set.
        replace_host (str or None): The host which should be used instead of the one which is in the data.
            This is only recommended on deploy process when your WMS might be already available on a DEV
            instance but not on the production system which is linked in the data. Then you can create legend
            entries by obtaining them from this DEV instance.
        replace_layer (str or None): The layer which should be used instead of the one which is in the data.
            This is only recommended on deploy process when your WMS might be already available on a DEV
            instance serving a special legend layer but not on the production system which is linked in
            the data. Then you can create legend entries by obtaining them from this DEV instances special
            legend layer.
        string_keys (bool): Switch for setting primary key for legend entries whether to string or integer
        by_type_code (bool): If set the process will use the type_code instead of name for obtaining the
            legend icons. This needs a WMS layer to be configured with the type_code in its name property. It
            prevents the legend entry creation process to be broken for case sensitive class names in
            MAPSERVER. Because the "RULE" parameter of the GetLegendGraphics request on MAPSERVER seems to be
            case insensitive.
    """

    # config object parsed from oereb configuration yml
    config = parse(config, section)
    db_connection = None
    found = False

    # try to find the topic in config and create the orm models for further processing
    for topic in config.get('plrs'):
        if topic.get('code') == topic_code:
            db_connection = topic.get('source').get('params').get('db_connection')
            Plr = DottedNameResolver().maybe_resolve(
                '{models_path}.PublicLawRestriction'.format(
                    models_path=topic.get('source').get('params').get('models')
                )
            )
            LegendEntry = DottedNameResolver().maybe_resolve(
                '{models_path}.LegendEntry'.format(
                    models_path=topic.get('source').get('params').get('models'))
            )
            found = True
            break
    if not found:
        # at this point it was not possible to find the topic in configuration
        print('The topic with code "{0}" was not found in passed configuration!'.format(topic_code))
        return

    # we can start process now...
    engine = create_engine(db_connection, echo=True)
    Session = orm.scoped_session(orm.sessionmaker(bind=engine))
    session = Session()

    # clean up table first
    session.execute('''TRUNCATE TABLE {schema}.{table} RESTART IDENTITY'''.format(
        schema=LegendEntry.__table__.schema,
        table=LegendEntry.__table__.name
    ))

    # select all plrs from distinct on information, view_service_id and type_code
    unique_plrs = session.query(Plr).distinct(
        Plr.view_service_id,
        Plr.type_code
    ).all()
    pyconizer_config = []
    type_code_list = []

    # first create the configuration for the pyconizer package
    for unique_plr in unique_plrs:
        if unique_plr.type_code not in type_code_list:
            type_code_list.append(unique_plr.type_code)
        url, params = parse_url(unique_plr.view_service.reference_wms)
        layer_existent = False
        service_url = urlunsplit((url.scheme, url.netloc, '', '', '')) \
            if replace_host is None else replace_host
        layer = params.get('LAYERS')[0] if replace_layer is None else replace_layer
        for layer_config in pyconizer_config:
            if layer_config.get('url') == service_url and \
                    layer_config.get('layer') == layer:
                layer_existent = True
        if not layer_existent:
            pyconizer_config.append({
                'url': service_url,
                'layer': layer,
                'get_styles': {
                    'request': 'GetStyles',
                    'service': 'WMS',
                    'srs': params.get('SRS'),
                    'version': params.get('VERSION')
                },
                'get_legend': {
                    'image_format': image_format,
                    'request': 'GetLegendGraphic',
                    'service': 'WMS',
                    'version': params.get('VERSION'),
                    'width': image_width,
                    'height': image_height
                }
            })

    # create the icons with pyconizer package
    create_icons_from_scratch(pyconizer_config, temp_creation_path, images=True, encoding=encoding)

    # reuse plr information to build legend entries and assign the symbol
    i = 1
    for unique_plr in unique_plrs:
        url, params = parse_url(unique_plr.view_service.reference_wms)
        layer = params.get('LAYERS')[0] if replace_layer is None else replace_layer

        # obtain symbol from pyconizer structure.
        if by_type_code:
            class_name = unique_plr.type_code
        else:
            if isinstance(unique_plr.information, dict):
                class_name = unique_plr.information.get(language)
            else:
                class_name = unique_plr.information
        symbol = get_icon(
            temp_creation_path,
            layer,
            class_name
        )
        if symbol:
            session.add(LegendEntry(
                id=str(i) if string_keys else i,
                symbol=symbol,
                legend_text=unique_plr.information,
                type_code=unique_plr.type_code,
                topic=unique_plr.topic,
                type_code_list=''.join(type_code_list),
                view_service_id=unique_plr.view_service_id
            ))
            session.flush()
            i += 1
        else:
            print(
                'WARNING: It was not possible to find a symbol for the class:',
                class_name.encode('utf-8')
            )
    session.commit()
    session.close()


def run():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create and insert legend entries for the specified theme.'
    )
    parser.add_option(
        '-c', '--configuration',
        dest='config',
        metavar='YAML',
        type='string',
        help='The absolute path to the configuration yaml file.'
    )
    parser.add_option(
        '-s', '--section',
        dest='section',
        metavar='SECTION',
        type='string',
        default='pyramid_oereb',
        help='The section which contains configuration (default is: pyramid_oereb).'
    )
    parser.add_option(
        '-t', '--theme',
        dest='topic_code',
        metavar='THEME_CODE',
        type='string',
        help='The theme code. Has to be available in configuration!'
    )
    parser.add_option(
        '-p', '--path',
        dest='temp_creation_path',
        metavar='TEMP_PATH',
        type='string',
        default='/tmp/pyconizer',
        help='Temporary working directory (default is: /tmp/pyconizer).'
    )
    parser.add_option(
        '-l', '--lang',
        dest='language',
        metavar='LANGUAGE',
        type='string',
        default='de',
        help='The language to use for multilingual data (default is: de).'
    )
    parser.add_option(
        '-f', '--format',
        dest='image_format',
        metavar='IMAGE_FORMAT',
        type='string',
        default='image/png',
        help='The format of the symbols to be created (default is: image/png).'
    )
    parser.add_option(
        '-H', '--height',
        dest='image_height',
        metavar='HEIGHT',
        type='int',
        default=36,
        help='The height in pixels of the symbols to be created (default is: 36).'
    )
    parser.add_option(
        '-W', '--width',
        dest='image_width',
        metavar='WIDTH',
        type='int',
        default=72,
        help='The width in pixels of the symbols to be created (default is: 72).'
    )
    parser.add_option(
        '-e', '--encoding',
        dest='encoding',
        metavar='ENCODING',
        type='str',
        default=None,
        help='The encoding which is used to encode the XML. Standard is None. This means the encoding is '
             'taken from the XML content itself. Only use this parameter if your XML content has no encoding '
             'set.'
    )
    parser.add_option(
        '-r', '--replacehost',
        dest='replace_host',
        metavar='REPLACEHOST',
        type='str',
        default=None,
        help='The host which should be used instead of the one which is in the data. This is only '
             'recommended on deploy process when your WMS might be already available on a DEV instance but '
             'not on the production system which is linked in the data. Then you can create legend entries '
             'by obtaining them from this DEV instance.'
    )
    parser.add_option(
        '-L', '--replacelayer',
        dest='replace_layer',
        metavar='REPLACELAYER',
        type='str',
        default=None,
        help='''The layer which should be used instead of the one which is in the data.
            This is only recommended on deploy process when your WMS might be already available on a DEV
            instance serving a special legend layer but not on the production system which is linked in
            the data. Then you can create legend entries by obtaining them from this DEV instances special
            legend layer.'''
    )
    parser.add_option(
        '-S', '--stringkeys',
        dest='string_keys',
        action='store_true',
        default=False,
        help='''Switch for setting primary key for legend entries whether to string or integer.'''
    )
    parser.add_option(
        '-T', '--bytypecode',
        dest='by_type_code',
        action='store_true',
        default=False,
        help='''If set the process will use the type_code instead of name for obtaining the
            legend icons. This needs a WMS layer to be configured with the type_code in its name property. It
            prevents the legend entry creation process to be broken for case sensitive class names in
            MAPSERVER. Because the "RULE" parameter of the GetLegendGraphics request on MAPSERVER seems to be
            case insensitive.'''
    )
    options, args = parser.parse_args()
    if not options.config:
        parser.error('No configuration file set.')
    if not options.topic_code:
        parser.error('No theme code defined.')
    try:
        create_legend_entries_in_standard_db(
            options.config,
            options.topic_code,
            temp_creation_path=options.temp_creation_path,
            language=options.language,
            section=options.section,
            image_format=options.image_format,
            image_height=options.image_height,
            image_width=options.image_width,
            encoding=options.encoding,
            replace_host=options.replace_host,
            replace_layer=options.replace_layer,
            string_keys=options.string_keys,
            by_type_code=options.by_type_code
        )
    except Exception as e:
        log.exception(e)
