# -*- coding: utf-8 -*-
import base64

from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import DottedNameResolver

from pyramid_oereb import database_adapter


def get_image(request):
    """
    Returns the image for the requested theme and type code from database.

    Args:
        request (pyramid.request.Request): The request containing the codes as matchdict parameters.

    Returns:
        pyramid.response.Response: The generated response object.
    """
    plr = None
    from pyramid_oereb import Config
    for p in Config.get('plrs'):
        if str(p.get('code')).lower() == str(request.matchdict.get('theme_code')).lower():
            plr = p
            break
    source_params = plr.get('source').get('params')
    session = database_adapter.get_session(source_params.get('db_connection'))
    model = DottedNameResolver().resolve('{module_}.{class_}'.format(
        module_=source_params.get('models'),
        class_='LegendEntry'
    ))
    legend_entry = session.query(model).filter_by(type_code=request.matchdict.get('type_code')).first()
    symbol = getattr(legend_entry, 'symbol', None)
    if symbol:
        response = request.response
        response.status_int = 200
        response.content_type = 'image/*'
        response.body = base64.b64decode(symbol)
        return response
    raise HTTPNotFound()
