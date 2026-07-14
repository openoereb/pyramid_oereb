# -*- coding: utf-8 -*-
import requests
from pyreproj import Reprojector
from requests import Response
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
        self._type: str = 'locations'
        self._proxies = kwargs.get('proxies')
        self._referer = kwargs.get('referer', None)
        self._origins: str | None = None
        if 'origins' in kwargs:
            origins = kwargs.get('origins')
            if isinstance(origins, list):
                origins = ','.join(origins)
            self._origins = origins
        else:
            self._origins = 'address'

    def read(self, params, street_name: str, zip_code:int, street_number: str | None = None) \
            -> list[AddressRecord]:
        """
        Queries an address using the federal GeoAdmin API location search.

        Args:
            params (pyramid_oereb.core.views.webservice.Parameter):
                The parameters of the extract request
            street_name (str):
                The name of the street
            zip_code (int):
                The postal code
            street_number (str | None):
                The house or street number

        Returns:
            list[pyramid_oereb.core.records.address.AddressRecord]:
                A list of address records matching the supplied search criteria.
        """
        headers: dict[str, str | None] = {}
        if self._referer is not None:
            headers.update({
                'Referer': self._referer
            })
        request_params: dict[str, str | None] = {
            'type': self._type,
            'origins': self._origins,
            'searchText': f'{zip_code} {street_name} {street_number}'
        }
        response: Response = requests.get(
            self._geoadmin_url,
            params=request_params,
            proxies=self._proxies,
            headers=headers,
            timeout=4
        )
        if response.status_code == requests.codes.ok:
            rp: Reprojector = Reprojector()
            srid: int = Config.get('srid')
            records: list[AddressRecord] = []
            data = response.json()
            if 'results' in data:
                for item in data.get('results'):
                    attrs = item.get('attrs')
                    if isinstance(attrs, dict) and attrs.get('origin') == 'address':
                        x, y = rp.transform((attrs.get('lat'), attrs.get('lon')), to_srs=srid)
                        records.append(AddressRecord(
                            street_name=street_name,
                            zip_code=zip_code,
                            street_number=street_number,
                            geom=Point(x, y)
                        ))
            return records
        else:
            response.raise_for_status()
            return []
