# -*- coding: utf-8 -*-
import pytest

from pyramid.path import AssetResolver
from mako.lookup import TemplateLookup


def xml_templates():
    a = AssetResolver('pyramid_oereb')
    resolver = a.resolve('core/renderer/extract/templates/xml')
    templates = TemplateLookup(
        directories=[resolver.abspath()],
        output_encoding='utf-8',
        input_encoding='utf-8'
    )
    return templates

@pytest.fixture(scope='session')
def template():
    xml_templates().get_template('geometry/line.xml')