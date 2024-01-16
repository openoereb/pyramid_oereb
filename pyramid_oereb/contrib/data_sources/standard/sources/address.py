# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource


class DatabaseSource(BaseDatabaseSource):

    def filter(self, query, params, street_name, zip_code, street_number):
        """
        The filter method only selects some specific results from the standard database structure.
        It uses SQL-Alchemy for querying via passed arguments.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            street_name (unicode): The name of the street for the desired address.
            zip_code (int): The postal zipcode for the desired address.
            street_number (str): The house or so called street number of the desired address.
        """
        filtered_query = query.filter(
            self._model_.street_name == street_name
        ).filter(
            self._model_.zip_code == zip_code
        ).filter(
            self._model_.street_number == street_number
        ).limit(1)

        return filtered_query
