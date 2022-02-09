# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.records.view_service import LegendEntryRecord
from pyramid_oereb.core.sources.legend import LegendBaseSource
from pyramid_oereb.core.records.image import ImageRecord


class DatabaseSource(BaseDatabaseSource, LegendBaseSource):

    def read(self, params, **kwargs):
        """
        Central method to read one legend entry.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            (kwargs): Arbitrary keyword arguments. It must contain the key 'type_code'.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            query = session.query(self._model_)
            if kwargs.get('type_code'):
                results = query.filter(
                    self._model_.type_code == kwargs.get('type_code')
                ).all()
            else:
                raise AttributeError('Necessary parameter is missing.')

            self.records = list()
            for result in results:
                self.records.append(LegendEntryRecord(
                    ImageRecord(result.symbol),
                    result.legend_text,
                    result.type_code,
                    result.type_code_list,
                    result.theme,
                    sub_theme=result.sub_theme,
                    view_service_id=result.view_service_id
                ))
        finally:
            session.close()
