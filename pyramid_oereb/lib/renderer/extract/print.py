# -*- coding: utf-8 -*-

import json
import requests
import urlparse
import logging

from pyramid_oereb import Config
from pyramid_oereb.lib.renderer.extract.json_ import Renderer


log = logging.getLogger('pyramid_oereb')


class PrintRenderer(Renderer):

    def __call__(self, value, system):
        """
        Returns the JSON encoded extract, according to the specification.

        Args:
            value (tuple): A tuple containing the generated extract record and the params
                dictionary.
            system (dict): The available system properties.

        Returns:
            str: The JSON encoded extract.
        """
        self._request = self.get_request(system)
        extract_dict = self._render(value[0], value[1])
        log.debug(extract_dict)
        extract_dict["features"] = {
            "features": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        600000, 20000
                                    ],
                                    [
                                        600100, 20000
                                    ],
                                    [
                                        600000, 20100
                                    ],
                                    [
                                        600000, 20000
                                    ]
                                ]
                            ]
                        },
                        "properties": {}
                    }
                ]
            }
        }
        spec = {
            "layout": "A4 portrait",
            "outputFormat": "pdf",
            "attributes": extract_dict,
        }

        response = self.get_response(system)

        if self._request.GET.get('getspec', 'no') != 'no':
            response.headers['Content-Type'] = 'application/json; charset=UTF-8'
            return json.dumps(spec, sort_keys=True, indent=4)

        print_result = requests.post(
            urlparse.urljoin(Config.get('print', {})['base_url'] + "/", 'buildreport.pdf'),
            headers={
                "Content-Type": "application/json; charset=UTF-8"
            },
            data=json.dumps(spec)
        )
        response.status_code = print_result.status_code
        response.headers = print_result.headers
        return print_result.content
