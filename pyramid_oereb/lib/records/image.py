# -*- coding: utf-8 -*-
import re

from filetype import filetype

from pyramid_oereb.lib import b64


class ImageRecord(object):

    VALID_FILE_TYPES = [
        'png',
        'svg'
    ]  # type: list

    SVG_PATTERN = re.compile(r'<svg(.|\n)+<\/svg>')  # type: re

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
        return b64.encode(self.content)

    @staticmethod
    def _validate_filetype(obj):
        """
        Checks for valid file type and returns extension and mime type.

        Args:
            obj (str, bytes, bytearray or readable): Path to the file, a readable object or the file's content
                as str, bytes or bytearray. See filetype documentation:
                https://h2non.github.io/filetype.py/v1.0.0/filetype.m.html

        Returns:
            tuple: The file's extension and mime type.

        Raises:
            TypeError: Raised if type is invalid or could not be recognized.
        """

        try:
            ft = filetype.guess(obj)
        except IOError:
            ft = None

        # Check for SVG content if filetype.guess fails
        if ft is None:

            # Test for readable object first
            try:
                content = obj.read()
            except AttributeError:
                # Test for file path
                try:
                    with open(obj) as f:
                        content = f.read()
                except Exception:
                    # Use input as content as last option
                    content = obj

            # Convert to string
            if isinstance(content, bytes) or isinstance(content, bytearray):
                content = content.decode('utf-8')

            # Check for SVG content
            if ImageRecord.SVG_PATTERN.search(content):
                result = ('svg', 'image/svg+xml')
            else:
                raise TypeError('Unrecognized file type')

        else:
            result = (ft.extension, ft.mime)

        # Check for extension in valid file types
        if result[0] not in ImageRecord.VALID_FILE_TYPES:
            raise TypeError('Invalid file type: {invalid}. Valid types are: {valid}.'.format(
                invalid=ft.extension,
                valid=ImageRecord.VALID_FILE_TYPES
            ))

        return result

    @staticmethod
    def get_extension(obj):
        """
        Checks for valid file type and returns its extension.

        Args:
            obj (str, bytes, bytearray or readable): Path to the file, a readable object or the file's content
                as str, bytes or bytearray. See filetype documentation:
                https://h2non.github.io/filetype.py/v1.0.0/filetype.m.html

        Returns:
            str: The file's extension.
        """
        return ImageRecord._validate_filetype(obj)[0]

    @staticmethod
    def get_mimetype(obj):
        """
        Checks for valid file type and returns its mime type.

        Args:
            obj (str, bytes, bytearray or readable): Path to the file, a readable object or the file's content
                as str, bytes or bytearray. See filetype documentation:
                https://h2non.github.io/filetype.py/v1.0.0/filetype.m.html

        Returns:
            str: The file's mime type.
        """
        return ImageRecord._validate_filetype(obj)[1]

    @property
    def mimetype(self):
        """
        Checks for valid file type and returns its extension.

        Returns:
            str: The file's extension.
        """
        return ImageRecord.get_mimetype(bytearray(self.content))

    @property
    def extension(self):
        """
        Checks for valid file type and returns its mime type.

        Returns:
            str: The file's mime type.
        """
        return ImageRecord.get_extension(bytearray(self.content))
