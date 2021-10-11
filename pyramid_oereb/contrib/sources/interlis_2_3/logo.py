# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.logo import LogoBaseSource
from pyramid_oereb.contrib.interlis.interlis_2_3_utils import from_multilingual_blob_to_dict


class DatabaseSource(BaseDatabaseSource, LogoBaseSource):

    def read(self):
        """
        Central method to read all logos.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.code,
                    from_multilingual_blob_to_dict(result.multilingual_blob)
                ))
        finally:
            session.close()
