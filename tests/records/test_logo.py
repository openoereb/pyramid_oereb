# -*- coding: utf-8 -*-
from pyramid_oereb.core.records.logo import LogoRecord
from pyramid_oereb.core.records.image import ImageRecord


def test_logo_init():
    test_image = ''.join([
        "iVBORw0KGgoAAAANSUhEUgAAAB4A",
        "AAAPCAIAAAB82OjLAAAAL0lEQVQ4",
        "jWNMTd3EQBvAwsDAkFPnS3VzpzRt",
        "ZqK6oXAwavSo0aNGjwCjGWlX8gEA",
        "FAQGFyQKGL4AAAAASUVORK5CYII="
    ])
    record = LogoRecord(
        u'ch.1234', {
            'de': test_image
        }
    )
    assert record.code == u'ch.1234'
    assert isinstance(record.image_dict['de'], ImageRecord)
    assert record.image_dict['de'].encode() == test_image
