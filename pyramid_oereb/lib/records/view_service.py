# -*- coding: utf-8 -*-
import warnings
import logging
import requests

from pyramid.config import ConfigurationError
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.url import add_url_params, parse_url
from pyramid_oereb.lib.url import uri_validator
from pyramid_oereb.lib.config import Config
from shapely.geometry.point import Point


log = logging.getLogger(__name__)


class LegendEntryRecord(object):
    """
    Represents a legend entry with it's text as well as it's image.

    Args:
        symbol (pyramid_oereb.lib.records.image.ImageRecord): The binary content of the legend symbol.
        legend_text (dict of unicode): The multilingual description text for the legend entry.
        type_code (unicode): The class of the legend entry corresponding to the plrs classes.
        type_code_list (unicode): An URL to the type code list.
        theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the legend entry belongs
            to.
        sub_theme (dict of unicode or None): Theme sub category.
        other_theme (unicode): Additional theme linked to this theme.
        view_service_id (int): The id to the connected view service. This is very important to be able to
            solve bug https://github.com/openoereb/pyramid_oereb/issues/521
    """

    def __init__(self, symbol, legend_text, type_code, type_code_list, theme, sub_theme=None,
                 other_theme=None, view_service_id=None):

        if not isinstance(legend_text, dict):
            warnings.warn('Type of "legend_text" should be "dict"')

        if sub_theme is not None and not isinstance(sub_theme, dict):
            warnings.warn('Type of "sub_theme" should be "dict"')

        self.symbol = symbol
        self.legend_text = legend_text
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.theme = theme
        self.view_service_id = view_service_id
        self.sub_theme = sub_theme
        self.other_theme = other_theme
        self.view_service_id = view_service_id

    def __str__(self):
        return '<{} -- symbol: {} legend_text: {} type_code: {} type_code_list: {}'\
                    ' theme: {} sub_theme: {} other_theme: {}'\
                    .format(self.__class__.__name__, self.symbol, self.legend_text,
                            self.type_code, self.type_code_list, self.theme,
                            self.sub_theme, self.other_theme)


class ViewServiceRecord(object):
    """
    A view service contains a valid WMS URL with a defined set of layers.

    Attributes:
        image (pyramid_oereb.lib.records.image.ImageRecord or None): Binary image content downloaded from WMS
            link.
    """

    # Attributes defined while processing
    image = None    # map image resulting from calling the wms link - binary

    def __init__(self, reference_wms, layer_index, layer_opacity, legend_at_web=None, legends=None):
        """

        Args:
            reference_wms (uri): The link URL to the actual service (WMS)
            layer_index (int): Layer index. Value from -1000 to +1000.
            layer_opacity (float): Opacity of layer. Value from 0.0 to 1.0.
            legend_at_web (dict of str): )A multilingual dictionary of links. Keys are the language, values
                are links leading to a WMS (get legend) describing document (png).
            legends (list of LegendEntry): A list of all relevant legend entries.
        """
        self.reference_wms = reference_wms
        self.legend_at_web = legend_at_web

        self.layer_index = self.sanitize_layer_index(layer_index)
        self.layer_opacity = self.sanitize_layer_opacity(layer_opacity)

        self.min_NS03 = None
        self.max_NS03 = None
        self.min_NS95 = None
        self.max_NS95 = None
        self.calculate_ns()
        self.check_min_max_attributes(self.min_NS03, 'min_NS03', self.max_NS03, 'max_NS03')
        self.check_min_max_attributes(self.min_NS95, 'min_NS95', self.max_NS95, 'max_NS95')

        if legends is None:
            self.legends = []
        else:
            for legend in legends:
                assert isinstance(legend.symbol, ImageRecord)
            self.legends = legends

    @staticmethod
    def sanitize_layer_index(layer_index):
        if layer_index and not isinstance(layer_index, int):
            warnings.warn('Type of "layer_index" should be "int"')
        if layer_index < -1000 or layer_index > 1000:
            error_msg = "layer_index should be >= -1000 and <= 1000, " \
                        "was: {layer_index}".format(layer_index=layer_index)
            log.error(error_msg)
            raise AttributeError(error_msg)
        return layer_index

    @staticmethod
    def sanitize_layer_opacity(layer_opacity):
        if layer_opacity and not isinstance(layer_opacity, float):
            warnings.warn('Type of "layer_opacity" should be "float"')
        if layer_opacity < 0.0 or layer_opacity > 1.0:
            error_msg = "layer_opacity should be >= 0.0 and <= 1.0, " \
                        "was: {layer_opacity}".format(layer_opacity=layer_opacity)
            log.error(error_msg)
            raise AttributeError(error_msg)
        return layer_opacity

    @staticmethod
    def check_min_max_attributes(min_point, min_name, max_point, max_name):
        if min_point is None and max_point is None:
            return
        if min_point is None or max_point is None:
            error_msg = 'Both {min_name} and {max_name} have to be defined'.format(min_name=min_name,
                                                                                   max_name=max_name)
            raise AttributeError(error_msg)
        if not isinstance(min_point, Point):
            raise AttributeError('Type of "{min_name}" should be "shapely.geometry.point.Point"'
                                 .format(min_name=min_name))
        if not isinstance(max_point, Point):
            raise AttributeError('Type of "{max_name}" should be "shapely.geometry.point.Point"'
                                 .format(max_name=max_name))
        if min_point.x > max_point.x or min_point.y > max_point.y:
            error_msg = 'Some value of {min_name} are larger than {max_name}'.format(min_name=min_name,
                                                                                     max_name=max_name)
            raise AttributeError(error_msg)

    @staticmethod
    def get_map_size(format):
        print_conf = Config.get_object_path('print', required=['basic_map_size',
                                            'pdf_dpi', 'pdf_map_size_millimeters'])
        if format != 'pdf':
            return print_conf['basic_map_size']
        else:
            pixel_size = print_conf['pdf_dpi'] / 25.4
            map_size_mm = print_conf['pdf_map_size_millimeters']
            return [pixel_size * map_size_mm[0], pixel_size * map_size_mm[1]]

    @staticmethod
    def get_bbox(geometry):
        """
        Return a bbox adapted for the map size specified in the print configuration
         and based on the geometry and a buffer (margin to add between the geometry
         and the border of the map).

        Args:
            geometry (list): The geometry (bbox) of the feature to center the map on.

        Returns:
            list: The bbox (meters) for the print.
        """
        print_conf = Config.get_object_path('print', required=['basic_map_size', 'buffer'])
        print_buffer = print_conf['buffer']
        map_size = print_conf['basic_map_size']
        map_width = float(map_size[0])
        map_height = float(map_size[1])

        if print_buffer * 2 >= min(map_width, map_height):
            error_msg_txt = 'Your print buffer ({}px)'.format(print_buffer)
            error_msg_txt += ' applied on each side of the feature exceed the smaller'
            error_msg_txt += ' side of your map {}px.'.format(min(map_width, map_height))
            raise ConfigurationError(error_msg_txt)

        geom_bounds = geometry.bounds
        geom_width = float(geom_bounds[2] - geom_bounds[0])
        geom_height = float(geom_bounds[3] - geom_bounds[1])

        geom_ration = geom_width / geom_height
        map_ration = map_width / map_height

        # If the format of the map is naturally adapted to the format of the geometry
        is_format_adapted = geom_ration > map_ration

        if is_format_adapted:
            # Part (percent) of the margin compared to the map width.
            margin_in_percent = 2 * print_buffer / map_width
            # Size of the margin in geom units.
            geom_margin = geom_width * margin_in_percent
            # Geom width with the margins (right and left).
            adapted_geom_width = geom_width + (2 * geom_margin)
            # Adapted geom height to the map height
            adapted_geom_height = (adapted_geom_width / map_width) * map_height
        else:
            # Part (percent) of the margin compared to the map height.
            margin_in_percent = 2 * print_buffer / map_height
            # Size of the margin in geom units.
            geom_margin = geom_height * margin_in_percent
            # Geom height with the buffer (top and bottom).
            adapted_geom_height = geom_height + (2 * geom_margin)
            # Adapted geom width to the map width
            adapted_geom_width = (adapted_geom_height / map_height) * map_width

        height_to_add = (adapted_geom_height - geom_height) / 2
        width_to_add = (adapted_geom_width - geom_width) / 2

        return [
            geom_bounds[0] - width_to_add,
            geom_bounds[1] - height_to_add,
            geom_bounds[2] + width_to_add,
            geom_bounds[3] + height_to_add,
        ]

    def get_full_wms_url(self, real_estate, format):
        """
        Returns the WMS URL to get the image.

        Args:
            real_estate (pyramid_oereb.lob.records.real_estate.RealEstateRecord): The Real
                Estate record.
            format (string): The format currently used. For 'pdf' format,
                the used map size will be adapted to the pdf format,

        Returns:
            str: The url used to query the WMS server.
        """

        assert real_estate.limit is not None

        map_size = self.get_map_size(format)
        bbox = self.get_bbox(real_estate.limit)
        self.reference_wms = add_url_params(self.reference_wms, {
            "BBOX": ",".join([str(e) for e in bbox]),
            "SRS": 'EPSG:{0}'.format(Config.get('srid')),
            "WIDTH": int(map_size[0]),
            "HEIGHT": int(map_size[1])
        })
        self.calculate_ns()
        return self.reference_wms

    def download_wms_content(self):
        """
        Simply downloads the image found behind the URL stored in the instance attribute "reference_wms".

        Raises:
            LookupError: Raised if the response is not code 200 or content-type
                doesn't contains type "image".
            AttributeError: Raised if the URL itself isn't valid at all.
        """
        main_msg = "Image for WMS couldn't be retrieved."
        if uri_validator(self.reference_wms):
            log.debug("Downloading image, url: {url}".format(url=self.reference_wms))
            try:
                response = requests.get(self.reference_wms, proxies=Config.get('proxies'))
            except Exception as ex:
                dedicated_msg = "An image could not be downloaded. URL was: {url}, error was " \
                                "{response}".format(
                                    url=self.reference_wms,
                                    response=ex
                                )
                log.error(dedicated_msg)
                raise LookupError(dedicated_msg)

            content_type = response.headers.get('content-type', '')
            if response.status_code == 200 and content_type.find('image') > -1:
                self.image = ImageRecord(response.content)
            else:
                dedicated_msg = "The image could not be downloaded. URL was: {url}, Response was " \
                                "{response}".format(
                                    url=self.reference_wms,
                                    response=response.content.decode('utf-8')
                                )
                log.error(main_msg)
                log.error(dedicated_msg)
                raise LookupError(dedicated_msg)
        else:
            dedicated_msg = "URL seems to be not valid. URL was: {url}".format(url=self.reference_wms)
            log.error(main_msg)
            log.error(dedicated_msg)
            raise AttributeError(dedicated_msg)

    def unique_update_legends(self, legend):
        """
        Uniquely append a legend to the legend entries. It checks if a legend entry with the same type code
         already exists in the legends of this instance.

        Args:
            legend (pyramid_oereb.lib.records.view_service.LegendEntryRecord): The legend entry which
                should be append to the list.
        """
        already_exist = False
        for item in self.legends:
            if item.type_code == legend.type_code:
                already_exist = True
                break
        if not already_exist:
            self.legends.append(legend)

    def calculate_ns(self):
        srid = Config.get_crs()
        if srid == u'epsg:2056':
            self.min_NS95, self.max_NS95 = self.get_bbox_from_url(self.reference_wms)
        if srid == u'epsg:21781':
            self.min_NS03, self.max_NS03 = self.get_bbox_from_url(self.reference_wms)

    @staticmethod
    def get_bbox_from_url(wms_url):
        """
        Parses wms url for BBOX parameter an returns these points as suitable values for ViewServiceRecord.
        Args:
            wms_url (str): wms url which includes a BBOX parameter to parse.

        Returns:
            set of two shapely.geometry.point.Point: min and max coordinates of bounding box.
        """
        _, params = parse_url(wms_url)
        bbox = params.get('BBOX')
        if bbox is None or len(bbox[0].split(',')) != 4:
            return None, None
        points = bbox[0].split(',')
        return Point(float(points[0]), float(points[1])), Point(float(points[2]), float(points[3]))
