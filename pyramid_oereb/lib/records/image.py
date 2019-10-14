# -*- coding: utf-8 -*-
import base64

from filetype import filetype


class ImageRecord(object):

    VALID_FILE_TYPES = [
        'png',
        'svg'
    ]

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

    @staticmethod
    def _validate_filetype(obj):
        """
        Checks for valid file type and returns extension and mime type.

        Args:
            obj ():
        :return:
        """

        try:
            ft = filetype.guess(obj)
        except IOError:
            ft = None

        if ft is None:

            try:
                content = obj.read()
            except AttributeError:
                try:
                    with open(obj) as f:
                        content = f.read()
                except Exception:
                    content = '{0}'.format(obj)

            content = content.strip()
            if content.startswith('<svg') and content.endswith('</svg>'):
                result = ('svg', 'image/svg+xml')
            else:
                raise TypeError('Unrecognized file type')

        else:
            result = (ft.extension, ft.mime)

        if result[0] not in ImageRecord.VALID_FILE_TYPES:
            raise TypeError('Invalid file type: {invalid}. Valid types are: {valid}.'.format(
                invalid=ft.extension,
                valid=ImageRecord.VALID_FILE_TYPES
            ))

        return result

    @staticmethod
    def get_extension(obj):
        return ImageRecord._validate_filetype(obj)[0]

    @staticmethod
    def get_mimetype(obj):
        return ImageRecord._validate_filetype(obj)[1]

    @property
    def mimetype(self):
        return ImageRecord.get_mimetype(bytearray(self.content))

    @property
    def extension(self):
        return ImageRecord.get_extension(bytearray(self.content))
