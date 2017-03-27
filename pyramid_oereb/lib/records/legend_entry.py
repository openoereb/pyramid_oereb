# -*- coding: utf-8 -*-

__author__ = 'Clemens Rudert'
__create_date__ = '27.03.17'


class LegendEntry(object):

    def __init__(self, symbol=None, legend_text=None, type_code=None, type_code_list=None, theme=None,
                 sub_theme=None, additional_theme=None):
        """

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
        :rtype: list
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