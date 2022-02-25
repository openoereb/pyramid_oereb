# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.document import DocumentBaseSource
from pyramid_oereb import Config


class DatabaseSource(BaseDatabaseSource, DocumentBaseSource):

    def read(self, office_records):
        """
        Central method to read all theme entries.

        Args:
            office_records (list of pyramid_oereb.core.records.office.OfficeRecord): The office records of
                the exact request.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()
            self.records = list()
            for result in results:
                office_record_match = None
                for office_record in office_records:
                    if office_record.identifier == result.office_id:
                        office_record_match = office_record
                        break
                self.records.append(
                    self._record_class_(
                        document_type=Config.get_main_document_type_by_data_code(
                            result.document_type
                        ),
                        index=result.index,
                        law_status=Config.get_main_law_status_by_data_code(
                            result.law_status
                        ),
                        title=result.title,
                        responsible_office=office_record_match,
                        published_from=result.published_from,
                        published_until=result.published_until,
                        text_at_web=result.text_at_web,
                        abbreviation=result.abbreviation,
                        official_number=result.official_number,
                        only_in_municipality=result.only_in_municipality,
                        article_numbers=None,
                        file=result.file,
                        identifier=result.id
                    )
                )
        finally:
            session.close()
