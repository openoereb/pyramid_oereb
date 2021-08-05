import pytest
from pyramid_oereb.views.webservice import PlrWebservice
from tests.mockrequest import MockRequest
from tests import pyramid_oereb_test_config


@pytest.mark.parametrize('params', [
    {
        'GNSS': '32.1244978460310,-19.917989937473'
    }, {
        'gnss': '32.1244978460310,-19.917989937473'
    }, {
        'GnsS': '32.1244978460310,-19.917989937473'
    }, {
        'EN': '32.1244978460310,-19.917989937473'
    }, {
        'en': '32.1244978460310,-19.917989937473'
    }, {
        'En': '32.1244978460310,-19.917989937473'
    }
])
def test_get_egrid_coord(params):
    with pyramid_oereb_test_config():
        request = MockRequest(
            current_route_url='http://example.com/oereb/getegrid/json'
        )

        # Add params to matchdict as the view will do it for /getegrid/{format}/
        request.matchdict.update({
          'format': u'json'
        })

        request.params.update(params)
        webservice = PlrWebservice(request)
        webservice.get_egrid()


@pytest.mark.parametrize('params', [
    {
        'GEOMETRY': 'true',
        'EGRID': 'TEST',
        'WITHIMAGES': 'true',
        'SIGNED': 'true'
    }, {
        'geometry': 'true',
        'egrid': 'TEST',
        'withimages': 'TRUE',
        'signed': 'TRUE'
    }, {
        'Geometry': 'True',
        'Egrid': 'TEST',
        'WithImages': 'True',
        'Signed': 'True'
    }, {
        'geoMETRY': 'TRUE',
        'egrID': 'TEST',
        'LANG': 'DE',
        'sIgNeD': 'tRuE'
    }, {
        'gEoMeTrY': 'tRuE',
        'eGrId': 'TEST',
        'lang': 'De'
    }, {
        'GEOMETRY': 'true',
        'EGRID': 'TEST',
        'LanG': 'de'
    }, {
        'GEOMETRY': 'true',
        'EGRID': 'TEST',
        'TOPICS': 'ContaminatedSites,RailwaysProjectPlanningZones'
    }, {
        'GEOMETRY': 'true',
        'EGRID': 'TEST',
        'topics': 'ContaminatedSites,RailwaysProjectPlanningZones'
    }, {
        'GEOMETRY': 'true',
        'EGRID': 'TEST',
        'ToPics': 'ContaminatedSites,RailwaysProjectPlanningZones'
    }, {
        'GEOMETRY': 'true',
        'EGRID': 'TEST',
        'topics': 'ContaminatedSites,RailwaysProjectPlanningZones',
        'WITHIMAGES': 'trUE',
        'LanG': 'dE'
    }
])
def test_get_extract_by_id(params):
    with pyramid_oereb_test_config() as pyramid_config:
        pyramid_config.add_renderer('pyramid_oereb_extract_json',
                                    'pyramid_oereb.lib.renderer.extract.json_.Renderer')
        request = MockRequest()
        request.matchdict.update({
            'format': 'JSON'
        })
        request.params.update(params)
        service = PlrWebservice(request)
        service.get_extract_by_id()
