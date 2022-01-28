import datetime
import io
from PIL import Image
from mako.template import Template
from pyramid.path import AssetResolver

from pyramid_oereb import route_prefix
from pyramid_oereb.core.records.office import OfficeRecord


def get_symbol(theme_code, sub_theme_code, view_service_id, type_code, theme_config):
    """
    Returns the symbol for the requested theme and type code from database. It queries the model
    for the legend entry pyramid_oereb.contrib.data_sources.standard.models.get_legend_entry

    Args:
        theme_code (str): The theme code.
        sub_theme_code (str or None): The sub_theme code.
        view_service_id (str): The ID linking to the view service.
        type_code (str): The type_code.
        theme_config (dict): The configuration of the theme how it was set up in the YAML.

    Returns:
        bytearray, str: The image content and the mimetype of image.
    """
    # produces a dummy image of the correct dimension grey filled
    image = Image.new("RGB", (72, 36), (128, 128, 128))
    output = io.BytesIO()
    image.save(output, format='PNG')
    return output.getvalue(), 'image/png'


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
    query = None
    if record.sub_theme:
        query = {'sub_theme_code': record.sub_theme.sub_code}
    return request.route_url(
        '{0}/image/symbol'.format(route_prefix),
        theme_code=record.theme.code,
        view_service_id=record.view_service_id,
        type_code=record.type_code,
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
        'layer_name': real_estate_config['visualisation']['layer']['name'],
        'identifier': params['egrid'],
        'stroke_opacity': real_estate_config['visualisation']['style']['stroke_opacity'],
        'stroke_color': real_estate_config['visualisation']['style']['stroke_color'],
        'stroke_width': real_estate_config['visualisation']['style']['stroke_width']
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