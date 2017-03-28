# -*- coding: utf-8 -*-

__author__ = 'Clemens Rudert'
__create_date__ = '27.03.17'


class LegendEntryRecord(object):

    def __init__(self, symbol=None, legend_text=None, type_code=None, type_code_list=None, theme=None,
                 sub_theme=None, additional_theme=None):
        """
        Represents a legend entry with it's text as well as it's image.
        :param symbol: The binary file content of the legend image.
        :type symbol: binary
        :param legend_text: The description text for the legend entry.
        :type legend_text: str
        :param type_code: The class of the legend entry corresponding to the plrs classes.
        :type type_code: str
        :param type_code_list: An URL to the type code list.
        :type type_code_list: str
        :param theme: The theme ???
        :type theme: str
        :param sub_theme: ???
        :type sub_theme: str
        :param additional_theme: ???
        :type additional_theme: str
        """
        if not (symbol and legend_text and type_code and type_code_list and theme):
            raise TypeError('Fields "symbol", "legend_text", "type_code", "type_code_list" and "theme" must '
                            'be defined. Got {0}, {1}, {2}, {3} and {4}.'.format(symbol, legend_text,
                                                                                 type_code, type_code_list,
                                                                                 theme))
        self.symbol = symbol
        self.legend_text = legend_text
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.theme = theme
        self.sub_theme = sub_theme
        self.additional_theme = additional_theme

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'symbol',
            'legend_text',
            'type_code',
            'type_code_list',
            'theme',
            'sub_theme',
            'additional_theme'
        ]


class ViewServiceRecord(object):

    def __init__(self, link_wms=None, legend_web=None, legends=None):
        """

        :param link_wms: The link URL to the actual service (WMS)
        :type link_wms: str
        :param legend_web: The link URL to the actual legend service (WMS get legend)
        :type legend_web: str
        :param legends: A list of all relevant legend entries.
        :type legends: list of LegendEntry
        """
        if not (link_wms and legend_web):
            raise TypeError('Fields "link_wms" and "legend_web" must be defined. Got {0} and {1}.'.format(
                link_wms, legend_web))
        self.link_wms = link_wms
        self.legend_web = legend_web
        if legends is None:
            self.legends = []
        else:
            self.legends = legends

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'link_wms',
            'legend_web',
            'legends'
        ]
