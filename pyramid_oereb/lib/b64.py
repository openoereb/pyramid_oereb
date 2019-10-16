# -*- coding: utf-8 -*-
import base64
import sys


PY3 = sys.version_info[0] >= 3


def encode(value):
    """
    Encodes the input value using base64 encoding.

    Args:
        value (basestring): The input value.

    Returns:
        basestring: The encoded value.
    """
    if PY3 and isinstance(value, str):
        encoded = base64.b64encode(value.encode('utf-8'))
    else:
        encoded = base64.b64encode(value)
    if PY3:
        return encoded.decode('ascii')
    else:
        return encoded


def decode(value):
    """
    Decodes the input value using base64 encoding.

    Args:
        value (basestring): The input value.

    Returns:
        basestring: The decoded value.
    """
    if PY3:
        return base64.b64decode(value.encode('ascii'))
    else:
        return base64.b64decode(value)
