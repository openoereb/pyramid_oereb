# -*- coding: utf-8 -*-
import base64
import datetime
import json

from mako import exceptions
from mako.template import Template
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from pyramid.path import AssetResolver, DottedNameResolver
from pyramid.response import Response
from sqlalchemy import cast, Text

from pyramid_oereb import Config, database_adapter, route_prefix
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord


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
    try:
        model = DottedNameResolver().resolve(source_params.get('model'))
        municipality = session.query(model).filter_by(fosnr=fosnr).first()
        if municipality:
            logo = getattr(municipality, 'logo', None)
            if logo:
                response = request.response
                response.status_int = 200
                response.content_type = 'image/*'
                response.body = base64.b64decode(logo.encode('ascii'))
                return response
        raise HTTPNotFound()
    finally:
        session.close()


def get_symbol(request):
    """
    Returns the symbol for the requested theme and type code from database.

    Args:
        request (pyramid.request.Request): The request containing the codes as matchdict parameters.

    Returns:
        pyramid.response.Response: The generated response object.
    """

    theme_code = request.matchdict.get('theme_code')

    plr = None
    for p in Config.get('plrs'):
        if str(p.get('code')).lower() == str(theme_code).lower():
            plr = p
            break

    if plr is None:
        raise HTTPNotFound('No theme with code {}.'.format(theme_code))

    source_params = plr.get('source').get('params')
    session = database_adapter.get_session(source_params.get('db_connection'))

    type_code = request.params.get('CODE')
    legend_text = request.params.get('TEXT')

    if type_code is None:
        raise HTTPBadRequest('Missing parameter CODE.')
    if legend_text is None:
        raise HTTPBadRequest('Missing parameter TEXT.')

    try:
        model = DottedNameResolver().resolve('{module_}.{class_}'.format(
            module_=source_params.get('models'),
            class_='LegendEntry'
        ))
        legend_entry = session.query(model).filter(
            cast(model.type_code, Text) == cast(type_code, Text),
            cast(model.legend_text, Text) == json.dumps(json.loads(
                base64.b64decode(legend_text).decode('unicode-escape'))).decode('unicode-escape')
        ).first()
        if legend_entry:
            symbol = getattr(legend_entry, 'symbol', None)
            if symbol:
                response = request.response
                response.status_int = 200
                response.content_type = 'image/*'
                response.body = base64.b64decode(symbol.encode('ascii'))
                return response
        raise HTTPNotFound()

    finally:
        session.close()


def get_symbol_ref(request, record):
    """
    Returns the link to the symbol of the specified public law restriction.

    Args:
        request (pyramid.request.Request): The current request instance.
        record (pyramid_oereb.lib.records.plr.PlrRecord or
            pyramid_oereb.lib.records.view_service.LegendEntryRecord): The record of the public law
            restriction to get the symbol reference for.

    Returns:
        uri: The link to the symbol for the specified public law restriction.
    """
    text = record.information if isinstance(record, PlrRecord) else record.legend_text
    text_encoded = base64.b64encode(json.dumps(text).encode('utf-8')).decode('ascii')
    return request.route_url(
        '{0}/image/symbol'.format(route_prefix),
        theme_code=record.theme.code,
        _query={
            'TEXT': text_encoded,
            'CODE': record.type_code
        }
    )


def get_surveying_data_provider(real_estate):
    """

    Args:
        real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate for which the
            provider of the surveying data should be delivered.
    Returns:
        provider (pyramid_oereb.lib.records.office.OfficeRecord): The provider who produced the used
            surveying data.
    """
    provider = OfficeRecord({u'de': u'This is only a dummy'})
    return provider


def get_surveying_data_update_date(real_estate):
    """
    Gets the date of the latest update of the used survey data data for the
    situation map. The method you find here is only matching the standard configuration. But you can provide
    your own one if your configuration is different. The only thing you need to take into account is that the
    input of this method is always and only a real estate record. And the output of this method must be a
    datetime.date object.

    Args:
        real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
            estate for which the last update date of the base data should be indicated

    Returns:
        update_date (datetime.datetime): The date of the last update of the cadastral base data
    """

    update_date = datetime.datetime.now()

    return update_date


def produce_sld_content(request):
    """
    This is the standard hook method to provide the sld content. Of course you can set it to another one. For
    instance to use another template. Or to use other parameters to provide the correctly constructed SLD.

    .. note:: What to know about this Method: REQUEST-Method: GET, parameters only as url parameters

    When you are replacing this method take care that it has to accept a pyramid request as input and must
    deliver a valid SLD wrapped in a pyramid response instance as output. It is in your responsibility.

    Args:
        request (pyramid.request.Request): The request from the pyramid application.

    Returns:
        pyramid.response.Response: The
    """
    response = request.response
    template = Template(
        filename=AssetResolver('pyramid_oereb').resolve('standard/templates/sld.xml').abspath(),
        input_encoding='utf-8',
        output_encoding='utf-8'
    )
    layer = Config.get_real_estate_config().get('visualisation').get('layer')
    template_params = {}
    template_params.update(Config.get_real_estate_config().get('visualisation').get('style'))
    template_params.update({'layer_name': layer.get('name')})
    template_params.update({'identifier': request.params.get('egrid')})
    try:
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/xml'
        response.body = template.render(**template_params)
        return response
    except Exception:
        response.content_type = 'text/html'
        response.body = exceptions.html_error_template().render()
        return response
