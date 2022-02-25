# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.map_layering import MapLayeringBaseSource


class DatabaseSource(BaseDatabaseSource, MapLayeringBaseSource):

    def read(self):
        """
        Central method to read all map layering entries.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.view_service,
                    result.layer_index,
                    result.layer_opacity
                ))
        finally:
            session.close()
