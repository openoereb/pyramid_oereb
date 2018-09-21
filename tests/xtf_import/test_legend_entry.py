# -*- coding: utf-8 -*-
from lxml.etree import XML

from pyramid_oereb.standard.xtf_import.legend_entry import LegendEntry


def test_init():
    legend_entry = LegendEntry('foo', 'bar', 'baz')
    assert legend_entry._session == 'foo'
    assert legend_entry._model == 'bar'
    assert legend_entry._topic_code == 'baz'


def test_parse_symbol():
    element = XML("""
    <LegendeEintrag>
        <Symbol>
            <BINBLBOX>test</BINBLBOX>
        </Symbol>
    </LegendeEintrag>
    """)
    legend_entry = LegendEntry('foo', 'bar', 'baz')
    assert legend_entry._parse_symbol(element, 'foo') is None
    assert legend_entry._parse_symbol(element, 'Symbol') == 'test'
