# -*- coding: utf-8 -*-
import warnings

from pyramid_oereb.lib.url import add_url_params

from pyramid_oereb.lib.config import Config


class LegendEntryRecord(object):

    def __init__(self, symbol, legend_text, type_code, type_code_list, theme, sub_theme=None,
                 additional_theme=None):
        """
        Represents a legend entry with it's text as well as it's image.

        :param symbol: The binary file content of the legend image.
        :type symbol: pyramid_oereb.lib.records.image.ImageRecord
        :param legend_text: The multilingual description text for the legend entry.
        :type legend_text: dict
        :param type_code: The class of the legend entry corresponding to the plrs classes.
        :type type_code: str
        :param type_code_list: An URL to the type code list.
        :type type_code_list: str
        :param theme: The theme to which the legend entry belongs to.
        :type  theme: pyramid_oereb.lib.records.theme.ThemeRecord
        :param sub_theme: Theme sub category.
        :type sub_theme: str
        :param additional_theme: Additional theme linked to this theme.
        :type additional_theme: str
        """
        if not isinstance(legend_text, dict):
            warnings.warn('Type of "legend_text" should be "dict"')

        self.symbol = symbol
        self.legend_text = legend_text
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.theme = theme
        self.sub_theme = sub_theme
        self.additional_theme = additional_theme


class ViewServiceRecord(object):
    # Attributes defined while processing
    image = None    # map image resulting from calling the wms link - binary

    def __init__(self, link_wms, legend_web, legends=None):
        """

        :param link_wms: The link URL to the actual service (WMS)
        :type link_wms: str
        :param legend_web: The link URL to the actual legend service (WMS get legend)
        :type legend_web: str
        :param legends: A list of all relevant legend entries.
        :type legends: list of LegendEntry
        """
        self.link_wms = link_wms
        self.legend_web = legend_web
        if legends is None:
            self.legends = []
        else:
            self.legends = legends

    @staticmethod
    def _get_bbox(geometry, map_size, print_buffer):
        width_buffer = (geometry.bounds[2] - geometry.bounds[0]) * print_buffer / 100
        height_buffer = (geometry.bounds[3] - geometry.bounds[1]) * print_buffer / 100
        print_bounds = [
            geometry.bounds[0] - width_buffer,
            geometry.bounds[1] - height_buffer,
            geometry.bounds[2] + width_buffer,
            geometry.bounds[3] + height_buffer,
        ]
        width = print_bounds[2] - print_bounds[0]
        height = print_bounds[3] - print_bounds[1]
        obj_ration = width / height
        print_ration = map_size[0] / map_size[1]
        if obj_ration > print_ration:
            to_add = (width / print_ration - height) / 2
            print_bounds[0] -= to_add
            print_bounds[2] += to_add
        else:
            to_add = (height * print_ration - width) / 2
            print_bounds[1] -= to_add
            print_bounds[3] += to_add
        return print_bounds

    def get_full_wms_url(self, real_estate):
        """
        Returns the WMS URL to get the image.

        :param real_estate: The Real Estate record.
        :type real_estate: pyramid_oereb.lob.records.real_estate.RealEstateRecord
        :return: The url used to query the WMS server.
        :rtype: str
        """

        assert real_estate.limit is not None

        if real_estate.limit is not None:
            print_conf = Config.get_object_path('print', required=['map_size', 'buffer'])
            map_size = print_conf['map_size']
            bbox = self._get_bbox(real_estate.limit, map_size, print_conf['buffer'])
            return add_url_params(self.link_wms, {
                "BBOX": ",".join([str(e) for e in bbox])
            })
        else:
            return self.link_wms
