# -*- coding: utf-8 -*-


class LegendEntryRecord(object):

    def __init__(self, symbol, legend_text, type_code, type_code_list, theme, sub_theme=None,
                 additional_theme=None):
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
        :param theme: The theme.
        :type theme: str
        :param sub_theme: Theme sub category.
        :type sub_theme: str
        :param additional_theme: Additional theme linked to this theme.
        :type additional_theme: str
        """
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

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in self.get_fields():
            value = getattr(self, key)
            if value:
                extract[key] = value
        return extract


class ViewServiceRecord(object):
    # Attributes defined while processing
    image = None    # map image resulting from calling the wms link - binary

    def __init__(self, link_wms, legend_web, legends=None):
        """
        :param link_wms: The link URL to the actual service (WMS)
        :type link_wms: str
        :param image: The map image resulting from calling the WMS link
        :type image: binary
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

    def to_extract(self, type_code=None):
        """
        Returns a dictionary with all available values needed for the extract.
        :param type_code: Filter referenced legend entries by the specified type code.
        :type type_code: str
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in ['link_wms', 'legend_web']:
            value = getattr(self, key)
            if value:
                extract[key] = value
        key = 'legends'
        legends = getattr(self, key)
        if legends and len(legends) > 0:
            if type_code:
                filtered = list()
                for legend in legends:
                    if legend.type_code == type_code:
                        filtered.append(legend.to_extract())
                extract[key] = filtered
            else:
                extract[key] = [legend.to_extract() for legend in legends]
        return extract
