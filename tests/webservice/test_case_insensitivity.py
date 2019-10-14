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
        'XY': '32.1244978460310,-19.917989937473'
    }, {
        'xy': '32.1244978460310,-19.917989937473'
    }, {
        'Xy': '32.1244978460310,-19.917989937473'
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
        webservice.get_egrid_coord()


@pytest.mark.parametrize('params', [
    {
        'WITHIMAGES': None
    }, {
        'withimages': None
    }, {
        'WithImages': None
    }, {
        'LANG': 'DE'
    }, {
        'lang': 'DE'
    }, {
        'LanG': 'DE'
    }, {
        'TOPICS': 'ContaminatedSites,RailwaysProjectPlanningZones'
    }, {
        'topics': 'ContaminatedSites,RailwaysProjectPlanningZones'
    }, {
        'ToPics': 'ContaminatedSites,RailwaysProjectPlanningZones'
    }, {
        'topics': 'ContaminatedSites,RailwaysProjectPlanningZones',
        'WITHIMAGES': None,
        'LanG': 'DE'
    }
])
def test_get_extract_by_id(params):
    with pyramid_oereb_test_config() as pyramid_config:
        pyramid_config.add_renderer('pyramid_oereb_extract_json',
                                    'pyramid_oereb.lib.renderer.extract.json_.Renderer')
        request = MockRequest()
        request.matchdict.update({
            'flavour': 'REDUCED',
            'format': 'JSON',
            'param1': 'GEOMETRY',
            'param2': 'TEST'
        })
        request.params.update(params)
        service = PlrWebservice(request)
        service.get_extract_by_id()
