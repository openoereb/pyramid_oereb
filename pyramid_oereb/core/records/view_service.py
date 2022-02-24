# -*- coding: utf-8 -*-
import warnings
import logging
import requests

from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.url import add_url_params, parse_url
from pyramid_oereb.core.url import uri_validator
from shapely.geometry.point import Point
from pyramid_oereb.core import get_multilingual_element

log = logging.getLogger(__name__)


class LegendEntryRecord(object):
    """
    Represents a legend entry with it's text as well as it's image.

    Attributes:
        symbol (pyramid_oereb.lib.records.image.ImageRecord): The binary content of the legend symbol.
        legend_text (dict of unicode): The multilingual description text for the legend entry.
        type_code (unicode): The class of the legend entry corresponding to the plrs classes.
        type_code_list (unicode): An URL to the type code list.
        theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the legend entry
            belongs.
        view_service_id (int): The id to the connected view service. This is very important to be able to
            solve bug https://github.com/openoereb/pyramid_oereb/issues/521
        sub_theme (pyramid_oereb.lib.records.theme.ThemeRecord): The optional sub theme to which the
            legend entry belongs.
        identifier (str): The identifier of the legend entry which might be used for linking to
                other elements.
    """

    def __init__(self, symbol, legend_text, type_code, type_code_list, theme,
                 view_service_id=None, sub_theme=None, identifier=None):
        """
        Args:
            symbol (pyramid_oereb.lib.records.image.ImageRecord): The binary content of the legend symbol.
            legend_text (dict of unicode): The multilingual description text for the legend entry.
            type_code (unicode): The class of the legend entry corresponding to the plrs classes.
            type_code_list (unicode): An URL to the type code list.
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the legend entry
                belongs.
            view_service_id (int): The id to the connected view service. This is very important to be able to
                solve bug https://github.com/openoereb/pyramid_oereb/issues/521
            sub_theme (pyramid_oereb.lib.records.theme.ThemeRecord): The optional sub theme to which the
                legend entry belongs.
            identifier (str): The identifier of the legend entry which might be used for linking to
                    other elements.
        """
        if not isinstance(legend_text, dict):
            warnings.warn('Type of "legend_text" should be "dict"')

        self.symbol = symbol
        self.legend_text = legend_text
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.theme = theme
        self.view_service_id = view_service_id
        self.sub_theme = sub_theme
        self.identifier = identifier

    def __str__(self):
        return '<{} -- symbol: {} legend_text: {} type_code: {} type_code_list: {}'\
                    ' theme: {} sub_theme: {} view_service_id: {} identifier: {}'\
                    .format(self.__class__.__name__, self.symbol, self.legend_text,
                            self.type_code, self.type_code_list, self.theme, self.sub_theme,
                            self.view_service_id, self.identifier)


class ViewServiceRecord(object):
    """
    A view service contains a valid WMS URL with a defined set of layers.

    Attributes:
        image (dict): multilingual dictionary containing the binary image
            (pyramid_oereb.core.records.image.ImageRecord) downloaded from WMS link for the
            requested (if any) or default language. Empty for an extract without images
    """

    def __init__(self, reference_wms, layer_index, layer_opacity, default_language,
                 srid, proxies=None, legends=None):
        """

        Args:
            reference_wms (dict): Multilingual dict with URLs to the actual service (WMS)
            layer_index (int): Layer index. Value from -1000 to +1000.
            layer_opacity (float): Opacity of layer. Value from 0.0 to 1.0.
            default_language (str): The default language which should be used for url selection.
            srid (int): The SRID which is used for the WMS.
            proxies (dict or None): The proxies which may be used
            legends (list of LegendEntry or None): A list of all relevant legend entries.
        """
        self.reference_wms = reference_wms
        self.image = dict()  # multilingual dict with binary map images resulting from calling the wms link

        self.layer_index = self.sanitize_layer_index(layer_index)
        self.layer_opacity = self.sanitize_layer_opacity(layer_opacity)

        self.min = None
        self.max = None
        self.calculate_ns()
        self.check_min_max_attributes(self.min, 'min', self.max, 'max')
        self.default_language = default_language
        self.srid = srid
        self.proxies = proxies

        if legends is None:
            self.legends = []
        else:
            for legend in legends:
                assert isinstance(legend.symbol, ImageRecord)
            self.legends = legends

    @staticmethod
    def sanitize_layer_index(layer_index):
        """
        Checks the validity of the layer index
        Arg:
           layer_index (int): index of the layer

        Returns:
            int: the layer index if it is an int berween -1000 and 1000.

        Raises:
            AttributeError if the index is out of bounds
        """
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
        """
        Checks the validity of the layer opacity
        Args:
            layer_opacity (float): the opacity used to draw the layer.

        Returns:
            float: the layer opacity if it is a float between 0 and 1

        Raises:
            AttributeError if the opacity is out of bounds.
        """
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
        """
        Checks the validity of a min and max point:
            - type check
            - min_point < max_point
        Args:
            min_point (shapely.geometry.point.Point): a point geometry
            min_name (): the name of the point
            max_point (shapely.geometry.point.Point): a point geometry
            max_name ():the name of the point

        Raises:
            AttributeError if one of the check fails
        """
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

    def get_full_wms_url(self, language, map_width, map_height, bbox):
        """
        Returns the WMS URL to get the image.

        Args:
            language (string): which language of the reference WMS should be used.
            map_width (int): Width of map in pixels.
            map_height (int): Height of map in pixels.
            bbox (list of float): Bounding box which defines the maps view.

        Returns:
            str: The url used to query the WMS server.
        """

        if language not in self.reference_wms:
            msg = f"No WMS reference found for the requested language ({language}), using default language"
            log.info(msg)
            language = self.default_language

        self.reference_wms[language] = add_url_params(
            get_multilingual_element(self.reference_wms, language), {
                "BBOX": ",".join([str(e) for e in bbox]),
                "SRS": 'EPSG:{0}'.format(self.srid),
                "WIDTH": map_width,
                "HEIGHT": map_height
            }
        )
        self.calculate_ns()

        return self.reference_wms

    def download_wms_content(self, language):
        """
        Downloads the image found behind the URL stored in the instance attribute "reference_wms"
        for the requested language

        Args:
            language (string): the language for which the image should be downloaded

        Raises:
            LookupError: Raised if the response is not code 200 or content-type
                doesn't contains type "image".
            AttributeError: Raised if the URL itself isn't valid at all.
        """
        main_msg = "Image for WMS couldn't be retrieved."

        if language not in self.reference_wms:
            msg = f"No WMS reference found for the requested language ({language}), using default language"
            log.info(msg)
            language = self.default_language

        wms = self.reference_wms.get(language)

        if uri_validator(wms):
            log.debug(f"Downloading image, url: {wms}")
            try:
                response = requests.get(wms, proxies=self.proxies)
            except Exception as ex:
                dedicated_msg = f"An image could not be downloaded. URL was: {wms}, error was {ex}"
                log.error(dedicated_msg)
                raise LookupError(dedicated_msg)

            content_type = response.headers.get('content-type', '')
            if response.status_code == 200 and content_type.find('image') > -1:
                self.image[language] = ImageRecord(response.content)
            else:
                dedicated_msg = f"The image could not be downloaded. URL was: {wms}, " \
                    f"Response was {response.content.decode('utf-8')}"
                log.error(main_msg)
                log.error(dedicated_msg)
                raise LookupError(dedicated_msg)
        else:
            dedicated_msg = f"URL seems to be not valid. URL was: {wms}"
            log.error(main_msg)
            log.error(dedicated_msg)
            raise AttributeError(dedicated_msg)

    def calculate_ns(self):
        self.min, self.max = self.get_bbox_from_url(self.reference_wms[list(self.reference_wms.keys())[0]])

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
