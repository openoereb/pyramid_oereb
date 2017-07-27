# -*- coding: utf-8 -*-
import base64


class ImageRecord(object):
    """
    The record to hold the binary information of a image.

    Args:
        content (binary): The binary information of this image as binary string.
    """
    def __init__(self, content):

        self.content = content

    def encode(self):
        """
        Returns the image as base64 encoded string.

        Returns:
            str: The encoded image.
        """
        return base64.b64encode(self.content).decode('ascii')
