# -*- coding: utf-8 -*-


class MapLayeringRecord(object):
    """
    Represents a map layering entry with the view service, layer index and layer opacity.

    Args:
        view_service (str): View service.
        layer_index (str): Index for sorting the layering of the view services within a theme.
        layer_opacity (str): Opacity of a view service.
    """
    def __init__(self, view_service, layer_index, layer_opacity):

        self.view_service = view_service
        self.layer_index = layer_index
        self.layer_opacity = layer_opacity
