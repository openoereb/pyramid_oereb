# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class RealEstateReader(object):

    def __init__(self, dotted_source_class_path, **params):
        source_class = DottedNameResolver().resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, **kwargs):
        self._source_.read(**kwargs)
        return self._source_.records
