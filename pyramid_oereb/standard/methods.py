# -*- coding: utf-8 -*-
import base64

from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import DottedNameResolver

from pyramid_oereb import database_adapter, Config


def get_logo(request):
    """
    Returns the requested logo.

    Args:
        request (pyramid.request.Request): The request containing the logo key matchdict parameter.

    Returns:
        pyramid.response.Response: The generated response object.
    """
    logo_key = request.matchdict.get('logo')
    if logo_key in Config.get('logo').keys():
        logo = Config.get_logo_config().get(logo_key)
        response = request.response
        response.status_int = 200
        response.content_type = 'image/*'
        response.body = logo.content
        return response
    raise HTTPNotFound('This logo does not exist.')


def get_municipality(request):
    """
    Returns the requested municipality logo from database.

    Args:
        request (pyramid.request.Request): The request containing the fosnr as matchdict parameter.

    Returns:
        pyramid.response.Response: The generated response object.
    """
    fosnr = request.matchdict.get('fosnr')
    source_params = Config.get_municipality_config().get('source').get('params')
    session = database_adapter.get_session(source_params.get('db_connection'))
    model = DottedNameResolver().resolve(source_params.get('model'))
    municipality = session.query(model).filter_by(fosnr=fosnr).first()
    if municipality:
        logo = getattr(municipality, 'logo', None)
        if logo:
            response = request.response
            response.status_int = 200
            response.content_type = 'image/*'
            response.body = base64.b64decode(logo)
            return response
    raise HTTPNotFound()


def get_symbol(request):
    """
    Returns the symbol for the requested theme and type code from database.

    Args:
        request (pyramid.request.Request): The request containing the codes as matchdict parameters.

    Returns:
        pyramid.response.Response: The generated response object.
    """
    plr = None
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
    if legend_entry:
        symbol = getattr(legend_entry, 'symbol', None)
        if symbol:
            response = request.response
            response.status_int = 200
            response.content_type = 'image/*'
            response.body = base64.b64decode(symbol)
            return response
    raise HTTPNotFound()
