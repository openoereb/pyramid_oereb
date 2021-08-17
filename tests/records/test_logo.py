# -*- coding: utf-8 -*-
from pyramid_oereb.lib import b64
from pyramid_oereb.lib.records.logo import LogoRecord
from pyramid_oereb.lib.records.image import ImageRecord


def test_logo_init():
    record = LogoRecord(u'ch.1234', {
        'de': b64.decode('iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII=')
        })
    assert record.code == u'ch.1234'
    assert record.image_dict == {
        'de': b64.decode('iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII=')
    }
    assert isinstance(record.image_dict['de'], ImageRecord)
