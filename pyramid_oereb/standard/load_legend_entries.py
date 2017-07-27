# -*- coding: utf-8 -*-

import sys

from pyconizer import create_icons_from_scratch, get_icon
from pyconizer.lib.url import parse_url
from pyramid.path import DottedNameResolver
from sqlalchemy import create_engine, orm, Text

from pyramid_oereb import parse

if sys.version_info.major == 2:
    from urlparse import urlunsplit
else:

    from urllib.parse import urlunsplit


def create_legend_entries_in_standard_db(config, topic_code, temp_creation_path='/tmp/pyconizer',
                                         language='de', section='pyramid_oereb', image_format='image/png',
                                         image_height=36, image_width=72):
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
    session.execute('''TRUNCATE TABLE {schema}.{table}'''.format(
        schema=LegendEntry.__table__.schema,
        table=LegendEntry.__table__.name
    ))

    # select all plrs from distinct on information, view_service_id and type_code
    unique_plrs = session.query(Plr).distinct(
        Plr.information.cast(Text),
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
        for layer_config in pyconizer_config:
            if layer_config.get('url') == urlunsplit((url.scheme, url.netloc, '', '', '')) and \
                            layer_config.get('layer') == params.get('LAYERS')[0]:
                layer_existent = True
        if not layer_existent:
            pyconizer_config.append({
                'url': urlunsplit((url.scheme, url.netloc, '', '', '')),
                'layer': params.get('LAYERS')[0],
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
    create_icons_from_scratch(pyconizer_config, temp_creation_path, images=True)

    # reuse plr information to build legend entries and assign the symbol
    for unique_plr in unique_plrs:
        url, params = parse_url(unique_plr.view_service.reference_wms)

        # obtain symbol from pyconizer structure.
        symbol = get_icon(
            temp_creation_path,
            params.get('LAYERS')[0],
            unique_plr.information.get(language)
        )
        if symbol:
            # TODO: Handle symbol assignment to PLR
            session.add(LegendEntry(
                symbol=symbol,
                legend_text=unique_plr.information,
                type_code=unique_plr.type_code,
                topic=unique_plr.topic,
                type_code_list=''.join(type_code_list),
                view_service_id=unique_plr.view_service_id
            ))
            session.flush()
        else:
            print(
                'WARNING: It was not possible to find a symbol for the class:',
                unique_plr.information.get(language).encode('utf-8')
            )
    session.commit()
    session.close()
