# -*- coding: utf-8 -*-
import logging
import binascii

from pyramid.httpexceptions import HTTPNotFound, HTTPServerError

from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser
from pyramid_oereb import database_adapter
from pyramid_oereb.core import b64
from pyramid_oereb.core.records.image import ImageRecord


log = logging.getLogger(__name__)


def get_symbol(params, theme_config):
    """
    Returns the symbol for the requested theme and type code from database. It queries the model
    for the legend entry pyramid_oereb.contrib.data_sources.standard.models.get_legend_entry

    Args:
        params (dict): The URL parameters which were handed over via request.
        theme_config (dict): The configuration of the theme how it was set up in the YAML.

    Returns:
        bytearray, str: The image content and the mimetype of image.
    Raises:
        HTTPNotFound
        HTTPServerError
    """
    try:
        identifier = params['identifier']
    except KeyError:
        log.error(
            f'No useful params for HookMethod was delivered. '
            f'Expected "identifier" in params. Sent params are:  {params}'
        )
        raise HTTPServerError

    config_parser = StandardThemeConfigParser(**theme_config)
    session = database_adapter.get_session(config_parser.db_connection)

    log_string = 'identifier: {}'.format(
        identifier
    )

    try:
        models = config_parser.get_models()
        model = models.LegendEntry
        legend_entry = session.query(model).filter(
            model.t_id == identifier
        ).one()
        if legend_entry:
            symbol = getattr(legend_entry, 'symbol', None)
            if symbol:
                if isinstance(symbol, str):
                    body = b64.decode(symbol)
                elif isinstance(symbol, bytes):
                    body = b64.decode(binascii.b2a_base64(symbol).decode('ascii'))
                else:
                    log.error(f'Symbol was not str nor bytes type but {type(symbol)}. this is not supported.')
                    raise HTTPServerError
                content_type = ImageRecord.get_mimetype(bytearray(body))
                return body, content_type
            else:
                log.error(f'No symbol definition is available for legend entry {log_string}')
                raise HTTPServerError
        else:
            log.error(f'No legend entry was found in data for {log_string}')
            raise HTTPNotFound
    finally:
        session.close()
