# -*- coding: utf-8 -*-
import logging

from pyramid.httpexceptions import HTTPInternalServerError

log = logging.getLogger(__name__)


def get_multilingual_element(value, language, not_null=True):
    multilingual_value = value.get(language, None)

    if multilingual_value is None and not_null:
        msg = 'Default language "{language}" is not available in: \n {element}'\
            .format(language=language, element=value)
        log.error(msg)
        raise HTTPInternalServerError()

    return multilingual_value
