# -*- coding: utf-8 -*-
from pyramid.path import AssetResolver
from mako.lookup import TemplateLookup


def xml_templates():
    a = AssetResolver('pyramid_oereb')
    resolver = a.resolve('lib/renderer/extract/templates/xml')
    templates = TemplateLookup(
        directories=[resolver.abspath()],
        output_encoding='utf-8',
        input_encoding='utf-8'
    )
    return templates
