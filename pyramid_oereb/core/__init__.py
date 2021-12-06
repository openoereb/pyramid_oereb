# -*- coding: utf-8 -*-
import logging
import traceback

from pyramid.httpexceptions import HTTPInternalServerError

log = logging.getLogger(__name__)


def get_multilingual_element(value, language, not_null=True):
    multilingual_value = value.get(language, None)

    if multilingual_value is None and not_null:
        msg = 'Default language "{language}" is not available in: \n {element}'\
            .format(language=language, element=value)
        log.error(msg)
        log.info("Call stack of failing get_multilingual_element:")
        for line in traceback.format_stack():
            log.info("{}".format(line))

        raise HTTPInternalServerError()

    return multilingual_value
