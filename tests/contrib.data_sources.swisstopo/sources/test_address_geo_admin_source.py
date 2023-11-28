import pytest
from unittest.mock import patch
from requests import HTTPError
from pyramid_oereb.contrib.data_sources.swisstopo.address import AddressGeoAdminSource


@pytest.fixture
def requests_get():
    with patch('requests.get') as mocked_function:

        class Response():
            def __init__(self):
                self.status_code = 200

            # Response from:
            # https://api3.geo.admin.ch/rest/services/api/SearchServer
            # ?type=locations&searchText=4410%20Mühlemattstrasse%2036

            def json(self):
                return {
                    "results": [
                        {
                            "attrs":
                            {
                                "detail": "muehlemattstrasse 36 4410 liestal 2829 liestal ch bl",
                                "featureId": "2355731_0",
                                "geom_quadindex": "021101213123030021322",
                                "geom_st_box2d":
                                    (
                                        "BOX(621861.1194661561 259852.35739866708,"
                                        "621861.1194661561 259852.35739866708)"
                                    ),
                                "label": "M\u00fchlemattstrasse 36 <b>4410 Liestal</b>",
                                "lat": 47.48907470703125,
                                "lon": 7.728708267211914,
                                "num": 36,
                                "objectclass": "",
                                "origin": "address",
                                "rank": 7,
                                "x": 259852.359375,
                                "y": 621861.125,
                                "zoomlevel": 10
                            },
                            "id": 1047846,
                            "weight": 4
                        }
                    ]
                }

        mocked_function.return_value = Response()

        yield Response


@pytest.fixture
def requests_get_bad_request():
    with patch('requests.get') as mocked_function:

        class Response():
            def __init__(self):
                self.status_code = 400

            def raise_for_status(self):
                raise HTTPError()

        mocked_function.return_value = Response()

        yield Response


def test_address_geo_admin_source_origin_in_kwarg():
    A = AddressGeoAdminSource(**{"origins": "address2"})
    assert A._origins == "address2"


def test_address_geo_admin_source_origin_not_in_kwarg():
    A = AddressGeoAdminSource(**{})
    assert A._origins == "address"


def test_address_geo_admin_source_response(requests_get):

    with patch('pyramid_oereb.core.config.Config._config', new={"srid": 2056}):
        street_name = 'Mühlemattstrasse'
        zip_code = 4410
        street_number = 36

        agas = AddressGeoAdminSource()
        agas.read(None, street_name, zip_code, street_number)

        assert len(agas.records) == 1
        assert agas.records[0].street_name == street_name
        assert agas.records[0].zip_code == zip_code
        assert agas.records[0].street_number == street_number
        assert abs(agas.records[0].geom.x - 2621861.6883699098) < 0.01
        assert abs(agas.records[0].geom.y - 1259852.8367522908) < 0.01


def test_address_geo_admin_source_response_bad_request(requests_get_bad_request):

    with pytest.raises(HTTPError):

        street_name = 'Mühlemattstrasse'
        zip_code = 4410
        street_number = 36

        agas = AddressGeoAdminSource()
        agas.read(None, street_name, zip_code, street_number)
