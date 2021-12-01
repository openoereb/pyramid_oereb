# -*- coding: utf-8 -*-
import requests
from pyreproj import Reprojector
from shapely.geometry import Point

from pyramid_oereb import Config
from pyramid_oereb.core.records.address import AddressRecord
from pyramid_oereb.core.sources.address import AddressBaseSource


class AddressGeoAdminSource(AddressBaseSource):
    """
    An address source that uses the federal GeoAdmin API to return the geo location of a postal address.
    """
    def __init__(self, **kwargs):
        """
        Creates a new AddressGeoAdminSource.

        Keyword Args:
            geoadmin_search_api (uri): Url of the GeoAdmin API's search service. (**required**)
            origins (str or list of str): Filter results by origin. Defaults to *address*. (**optional**)
            referer (str): Referer to use. (**optional**)
            proxies (dict): Proxy definition according to
                http://docs.python-requests.org/en/master/user/advanced/#proxies. (**optional**)
        """
        super(AddressGeoAdminSource, self).__init__()
        self._geoadmin_url = kwargs.get('geoadmin_search_api',
                                        'https://api3.geo.admin.ch/rest/services/api/SearchServer')
        self._type = 'locations'
        self._proxies = kwargs.get('proxies')
        self._referer = kwargs.get('referer', None)
        if 'origins' in kwargs:
            origins = kwargs.get('origins')
            if isinstance(origins, list):
                origins = ','.join(origins)
            self._origins = origins
        else:
            self._origins = 'address'

    def read(self, params, street_name, zip_code, street_number):
        """
        Queries an address using the federal GeoAdmin API location search.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            street_name (unicode): The name of the street for the desired address.
            zip_code (int): The postal zipcode for the desired address.
            street_number (unicode): The house or so called street number of the desired address.
        """
        headers = {}
        if self._referer is not None:
            headers.update({
                'Referer': self._referer
            })
        request_params = {
            'type': self._type,
            'origins': self._origins,
            'searchText': u'{0} {1} {2}'.format(zip_code, street_name, street_number)
        }
        response = requests.get(
            self._geoadmin_url,
            params=request_params,
            proxies=self._proxies,
            headers=headers
        )
        if response.status_code == requests.codes.ok:
            rp = Reprojector()
            srid = Config.get('srid')
            self.records = list()
            data = response.json()
            if 'results' in data:
                for item in data.get('results'):
                    attrs = item.get('attrs')
                    if isinstance(attrs, dict) and attrs.get('origin') == 'address':
                        x, y = rp.transform((attrs.get('lat'), attrs.get('lon')), to_srs=srid)
                        self.records.append(AddressRecord(
                            street_name=street_name,
                            zip_code=zip_code,
                            street_number=street_number,
                            geom=Point(x, y)
                        ))
        else:
            response.raise_for_status()
