# -*- coding: utf-8 -*-
import warnings

from pyramid_oereb.core import b64

from pyramid_oereb.core.records.image import ImageRecord


class LogoRecord(object):
    """
    Represents a logo with its code and its base64 encoded string (multilingual).

    Attributes:
        code (str of unicode): The code for the logo.
        image_dict (dict of pyramid_oereb.lib.records.image.ImageRecord): The image encoded
            as base64 (multilingual).
    """
    def __init__(self, code, image_dict):
        """
        Args:
            code (str of unicode): The code for the logo.
            image_dict (dict of pyramid_oereb.lib.records.image.ImageRecord): The image encoded
                as base64 (multilingual).
        """

        if not isinstance(code, str):
            warnings.warn('Type of "code" should be "str"')
        if not isinstance(image_dict, dict):
            warnings.warn('Type of "image_dict" should be "dict"')

        self.code = code
        self.image_dict = {}
        for key in image_dict.keys():
            self.image_dict[key] = ImageRecord(b64.decode(image_dict[key]))
