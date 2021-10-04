# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.theme import ThemeBaseSource
from pyramid_oereb import Config


class DatabaseSource(BaseDatabaseSource, ThemeBaseSource):

    def from_db_to_document_records(self, documents_from_db, article_numbers=None):
        document_records = []
        for i, document in enumerate(documents_from_db):
            office_record = self.from_db_to_office_record(document.responsible_office)

            article_nrs = article_numbers[i] if isinstance(article_numbers, list) else None
            law_status = Config.get_law_status_by_code(
                self._plr_info.get('code'),
                document.law_status
            )
            document_records.append(self._documents_record_class(
                document_type=document.document_type,
                index=document.index,
                law_status=law_status,
                title=document.title,
                responsible_office=office_record,
                published_from=document.published_from,
                published_until=document.published_until,
                text_at_web=document.text_at_web,
                abbreviation=document.abbreviation,
                official_number=document.official_number,
                only_in_municipality=document.only_in_municipality,
                article_numbers=article_nrs,
                file=document.file
            ))
        return document_records

    def get_document_records(self, theme_from_db):
        documents_from_db = []
        article_numbers = []
        if not hasattr(theme_from_db, 'legal_provisions'):
            raise AttributeError('The public_law_restriction implementation of type {} has no '
                                 'legal_provisions attribute. Check the model implementation.'
                                 .format(type(theme_from_db)))
        for legal_provision in theme_from_db.legal_provisions:
            documents_from_db.append(legal_provision.document)
            article_nrs = legal_provision.articles['articles'] if legal_provision.articles \
                else None
            article_numbers.append(article_nrs)
        document_records = self.from_db_to_document_records(documents_from_db, article_numbers)
        return document_records

    def read(self):
        """
        Central method to read all theme entries.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            results = session.query(self._model_).all()

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.code,
                    result.title,
                    result.extract_index,
                    result.sub_code,
                    self.get_document_records(result)
                ))
        finally:
            session.close()
