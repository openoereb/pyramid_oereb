import datetime
import re
from mako.template import Template
from pyramid.path import AssetResolver

from pyramid_oereb import route_prefix
from pyramid_oereb.core.records.office import OfficeRecord


def get_symbol(params, theme_config):
    """
    This is a dummy method only to define what is expected by the real implementation.

    It is expected that this method delivers the actual binary content of the found image
    and the mime type fitting to the image content.

    Args:
        params (dict): The URL parameters which were handed over via request.
        theme_config (dict): The configuration of the theme how it was set up in the YAML.

    Returns:
        bytearray, str: The image content and the mimetype of image.
    """
    raise NotImplementedError('Method has to be implemented.')


def get_symbol_ref(request, record):
    """
    Returns the link to the symbol of the specified public law restriction.

    Args:
        request (pyramid.request.Request): The current request instance.
        record (pyramid_oereb.core.records.view_service.LegendEntryRecord): The legend entry record to get
            the symbol reference (link/url) for.

    Returns:
        uri: The link to the symbol for the specified public law restriction.
    """
    query = {
        'identifier': record.identifier
    }
    return request.route_url(
        '{0}/image/symbol'.format(route_prefix),
        theme_code=record.theme.code,
        extension=record.symbol.extension,
        _query=query
    )


def get_surveying_data_provider(real_estate):
    """

    Args:
        real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate for which the
            provider of the surveying data should be delivered.
    Returns:
        provider (pyramid_oereb.core.records.office.OfficeRecord): The provider who produced the used
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


def produce_sld_content(params, real_estate_config):
    """
    This is the standard hook method to provide the sld content. Of course you can set it to another one. For
    instance to use another template. Or to use other parameters to provide the correctly constructed SLD.

    The SLD can be used as Styling parameter to the WMS call to produce a highlighted real estate.

    When you are replacing this method take care that it has to accept the parameters as defined here as input
    and must deliver a valid SLD. It is in your responsibility.

    Args:
        params (dict): The URL params which are passed.
        real_estate_config (dict): The configuration of the real estate how it was set up in the YAML.

    Returns:
        str: The rendered SLD (XML) as text.
    """
    template = Template(
        filename=AssetResolver('pyramid_oereb').resolve('core/views/templates/sld.xml').abspath(),
        input_encoding='utf-8',
        output_encoding='utf-8'
    )
    template_params = {
        'layer_name': re.sub(
            '<.*?>', '', real_estate_config['visualisation']['layer']['name'], flags=re.DOTALL
        ),
        'identifier': re.sub(
            '<.*?>', '', params['egrid'], flags=re.DOTALL
        ),
        'stroke_opacity': re.sub(
            '<.*?>', '', real_estate_config['visualisation']['style']['stroke_opacity'], flags=re.DOTALL
        ),
        'stroke_color': re.sub(
            '<.*?>', '', real_estate_config['visualisation']['style']['stroke_color'], flags=re.DOTALL
        ),
        'stroke_width': re.sub(
            '<.*?>', '', real_estate_config['visualisation']['style']['stroke_width'], flags=re.DOTALL
        )
    }
    return template.render(**template_params)


def plr_sort_within_themes(extract):
    """
    This is the standard hook method to sort a plr list (while respecting the theme order).
    This standard hook does no sorting, you can set your configuration to a different method if you need a
    specific sorting.

    Args:
        extract (pyramid_oereb.lib.records.extract.ExtractRecord): The unsorted extract

    Returns:
        pyramid_oereb.lib.records.extract.ExtractRecord: Returns the updated extract
    """
    return extract
