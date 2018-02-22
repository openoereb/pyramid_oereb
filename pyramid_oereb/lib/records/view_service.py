# -*- coding: utf-8 -*-

import warnings
import logging
import requests

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.url import add_url_params
from pyramid_oereb.lib.url import uri_validator
from pyramid_oereb.lib.config import Config


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
        sub_theme (unicode): Theme sub category.
        other_theme (unicode): Additional theme linked to this theme.
    """

    def __init__(self, symbol, legend_text, type_code, type_code_list, theme, sub_theme=None,
                 other_theme=None):

        if not isinstance(legend_text, dict):
            warnings.warn('Type of "legend_text" should be "dict"')

        self.symbol = symbol
        self.legend_text = legend_text
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.theme = theme
        self.sub_theme = sub_theme
        self.other_theme = other_theme

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

    def __init__(self, reference_wms, legend_at_web=None, legends=None):
        """

        Args:
            reference_wms (uri): The link URL to the actual service (WMS)
            legend_at_web (uri): The link URL to the actual legend service (WMS get legend)
            legends (list of LegendEntry): A list of all relevant legend entries.
        """
        self.reference_wms = reference_wms
        self.legend_at_web = legend_at_web
        if legends is None:
            self.legends = []
        else:
            for legend in legends:
                assert isinstance(legend.symbol, ImageRecord)
            self.legends = legends

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

        geom_bounds = geometry.bounds
        geom_width = float(geom_bounds[2] - geom_bounds[0])
        geom_height = float(geom_bounds[3] - geom_bounds[1])

        geom_ration = geom_width / geom_height
        map_ration = map_width / map_height

        # If the format of the map is naturally adapted to the format of the geometry
        is_format_adapted = geom_ration < map_ration

        if is_format_adapted:
            map_height_without_buffer = map_height - 2 * print_buffer
            # Calculate the new height of the geom with the buffer.
            geom_height_with_buffer = map_height / map_height_without_buffer * geom_height
            # Calculate the new geom width with the map ratio and the new geom height.
            geom_width_with_buffer = geom_height_with_buffer * map_ration
        else:
            map_width_without_buffer = map_width - 2 * print_buffer
            # Calculate the new width of the geom with the buffer.
            geom_width_with_buffer = map_width / map_width_without_buffer * geom_width
            # Calculate the new geom height with the map ratio and the new geom width.
            geom_height_with_buffer = geom_width_with_buffer * map_ration

        height_to_add = (geom_height_with_buffer - geom_height) / 2
        width_to_add = (geom_width_with_buffer - geom_width) / 2

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
        return self.reference_wms

    def download_wms_content(self):
        """
        Simply downloads the image found behind the URL stored in the instance attribute "reference_wms".

        Raises:
            LookupError: Raised if the response is not code 200
            AttributeError: Raised if the URL itself isn't valid at all.
        """
        # TODO: Check better for a image as response than only code 200...
        main_msg = "Image for WMS couldn't be retrieved."
        if uri_validator(self.reference_wms):
            response = requests.get(self.reference_wms, proxies=Config.get('proxies'))
            if response.status_code == 200:
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
