# -*- coding: utf-8 -*-
import datetime

from mako import exceptions
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response

from pyramid_oereb import Config
from pyramid_oereb.lib.records.office import OfficeRecord


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

    .. note:: What to know about this Method: REQUEST-Method: GET, parameters only over url parameters

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
    except:
        response.content_type = 'text/html'
        response.body = exceptions.html_error_template().render()
        return response
