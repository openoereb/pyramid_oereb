# -*- coding: utf-8 -*-
import base64
import os

from pyramid_oereb.lib.adapter import FileAdapter


class ImageRecord(object):

    def __init__(self, content, source=None):
        """
        The record to hold the binary information of a image.

        Args:
            content (binary): The binary information of this image as binary string.
            source (str): The source of the image to generate a URL on rendering.
        """
        self.content = content
        self.source = os.path.abspath(source) if source else None

    def encode(self):
        """
        Returns the image as base64 encoded string.

        Returns:
            str: The encoded image.
        """
        return base64.b64encode(self.content)

    def get_url(self, request):
        """
        Returns the static URL for this image.

        Args:
            request (pyramid.request.Request): The extract request.

        Returns:
            str: The static URL for this image.
        """
        return request.static_url(self.source) if self.source else None

    @staticmethod
    def from_file(path):
        """
        Creates an image record from file.

        Args:
            path (str): Path to the image file.

        Returns:
            ImageRecord: A new image record instance created from the file.
        """
        file_adapter = FileAdapter()
        return ImageRecord(file_adapter.read(path), path)
