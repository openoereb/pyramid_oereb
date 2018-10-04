# -*- coding: utf-8 -*-
import math

import pytest
from lxml.etree import XML

from pyramid_oereb.standard.xtf_import.util import get_tag, parse_ref, parse_string, \
    parse_multilingual_text, parse_article_numbers, stroke_arc, get_angle


def test_get_tag():
    el = XML("""
    <bar></bar>
    """)
    assert get_tag(el) == 'bar'


def test_parse_ref():
    el = XML("""
    <bar REF="foo"></bar>
    """)
    assert parse_ref([el], 'bar') == 'foo'
    assert parse_ref([el], 'baz') is None


def test_parse_string():
    element = XML("""
    <Element>
        <Property>Value</Property>
    </Element>
    """)
    assert parse_string(element, 'foo') is None
    assert parse_string(element, 'Property') == 'Value'


def test_parse_multilingual_text():
    element = XML("""
    <Element>
        <Property>
            <MultilingualText>
                <LocalizedText>
                    <LocalisationCH_V1.LocalisedText>
                        <Language>de</Language>
                        <Text>Test</Text>
                    </LocalisationCH_V1.LocalisedText>
                </LocalizedText>
            </MultilingualText>
        </Property>
    </Element>
    """)
    assert parse_multilingual_text(element, 'foo') is None
    assert parse_multilingual_text(element, 'Property') == {
        'de': 'Test'
    }


def test_parse_article_numbers():
    doc = XML("""
    <Document>
        <Artikel>
            <Nr>nr1</Nr>
            <Nr>nr2</Nr>
        </Artikel>
    </Document>
    """)
    assert parse_article_numbers(doc, 'foo') is None
    assert parse_article_numbers(doc, 'Artikel') == 'nr1|nr2'


@pytest.mark.parametrize('start,arc,end,max_diff,precision,count,expected', [
    ((0, 0), (1, 1), (2, 0), 0.1, 3, 4, [
        (0.293, 0.707),
        (1.0, 1.0),
        (1.707, 0.707),
        (2.0, 0.0)
    ]),
    ((0, 1), (1, 0), (2, 1), 0.1, 3, 4, [
        (0.293, 0.293),
        (1.0, 0.0),
        (1.707, 0.293),
        (2.0, 1.0)
    ]),
    ((-1, -1), (0, 0), (-1, 1), 0.1, 3, 4, [
        (-0.293, -0.707),
        (0.0, 0.0),
        (-0.293, 0.707),
        (-1.0, 1.0)
    ]),
    ((-1, 0), (0, 1), (1, 0), 0.001, 3, 36, None),
    ((-1, 0), (0, 1), (1, 0), 0.001, 1, 32, None)
])
def test_stroke_arc(start, arc, end, max_diff, precision, count, expected):
    result = stroke_arc(start, arc, end, max_diff, precision)
    assert len(result) == count
    if expected is not None:
        assert result == expected


@pytest.mark.parametrize('d_start,d_arc,d_end,diff,rot', [
    (0.0, 0.5 * math.pi, math.pi, math.pi, 1),
    (1.5 * math.pi, 0.1 * math.pi, 0.5 * math.pi, math.pi, 1),
    (0.5 * math.pi, 0.1 * math.pi, 1.5 * math.pi, math.pi, -1)
])
def test_get_angle(d_start, d_arc, d_end, diff, rot):
    assert get_angle(d_start, d_arc, d_end) == (diff, rot)
