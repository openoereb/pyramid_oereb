# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.document import DocumentBaseSource
from pyramid_oereb import Config


class DatabaseSource(BaseDatabaseSource, DocumentBaseSource):

    def read(self):
        """
        Central method to read all theme entries.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._documents_record_class(
                document_type=Config.get_document_type_by_code(
                    document.document_type
                ),
                index=document.index,
                law_status=Config.get_document_type_by_code(
                    document.law_status
                ),
                title=document.title,
                responsible_office=office_record,
                published_from=document.published_from,
                published_until=document.published_until,
                text_at_web=document.text_at_web,
                abbreviation=document.abbreviation,
                official_number=document.official_number,
                only_in_municipality=document.only_in_municipality,
                article_numbers=None,
                file=document.file,
                identifier=document.id
            ))
        finally:
            session.close()
