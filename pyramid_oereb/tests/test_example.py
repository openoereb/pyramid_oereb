import pytest
from pyramid.testing import DummyRequest
import json
from xml.etree import ElementTree


def read_request(table, format='json', schema='public'):
    request = DummyRequest(path="/api/{schema}/{table}/read/{format}".
                           format(schema=schema, table=table, format=format))
    request.matchdict['schema_name'] = schema
    request.matchdict['table_name'] = table
    request.matchdict['format'] = format
    return request


@pytest.mark.parametrize("format,parser", [
    ("json", json.loads),
    ("geojson", json.loads),
    ("xml", ElementTree.fromstring)
])
def test_read(example_api, format, parser):
    request = read_request('example', format=format)
    result = example_api.read(request)
    assert result.status_code == 200
    print("result=" + repr(result.text))
    parser(result.text)
