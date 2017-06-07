# -*- coding: utf-8 -*-
import base64


class ImageRecord(object):

    def __init__(self, content):
        """
        The record to hold the binary information of a image.

        :param content: The binary information of this image as binary string.
        :type content: str
        """
        self.content = content

    def encode(self):
        """
        Returns the image as base64 encoded string.

        :return: The encoded image.
        :rtype: str
        """
        return base64.b64encode(self.content)
