# -*- coding: utf-8 -*-

from pyramid_oereb.contrib.print_proxy.sub_themes.sorting import BaseSort, AlphabeticSort, ListSort


def theme1():
    return [
        {
            'SubTheme': u'\xd6REB'
        },
        {
            'SubTheme': u'123456'
        },
        {
            'SubTheme': u'zzzAAABBB'
        },
        {
            'SubTheme': u'ZZZAAABBB'
        },
        {
            'SubTheme': u'bbbZZZyyy'
        },
        {
            'SubTheme': u'aaaZZZyyy'
        }
    ]


def test_base_sort():
    expected = theme1()
    actual = BaseSort.sort(theme1(), {})
    for idx, val in enumerate(actual):
        assert val['SubTheme'] == expected[idx]['SubTheme']


def test_alphabetic_sort():
    expected = [
        {
            'SubTheme': u'123456'
        },
        {
            'SubTheme': u'aaaZZZyyy'
        },
        {
            'SubTheme': u'bbbZZZyyy'
        },
        {
            'SubTheme': u'\xd6REB'
        },
        {
            'SubTheme': u'zzzAAABBB'
        },
        {
            'SubTheme': u'ZZZAAABBB'
        }
    ]
    actual = AlphabeticSort.sort(theme1(), {})
    for idx, val in enumerate(actual):
        assert val['SubTheme'] == expected[idx]['SubTheme']


def test_list_sort():
    params = {
        'list': [
            u'ZZZAAABBB',
            u'\xd6REB',
            u'aaaZZZyyy'
        ]
    }
    expected = [
        {
            'SubTheme': u'ZZZAAABBB'
        },
        {
            'SubTheme': u'\xd6REB'
        },
        {
            'SubTheme': u'aaaZZZyyy'
        },
        {
            'SubTheme': u'123456'
        },
        {
            'SubTheme': u'zzzAAABBB'
        },
        {
            'SubTheme': u'bbbZZZyyy'
        }
    ]
    actual = ListSort.sort(theme1(), params)
    for idx, val in enumerate(actual):
        assert val['SubTheme'] == expected[idx]['SubTheme']
