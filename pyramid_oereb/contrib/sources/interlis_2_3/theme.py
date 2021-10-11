# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.theme import ThemeBaseSource
from pyramid_oereb.contrib.interlis.interlis_2_3_utils import from_multilingual_text_to_dict
from pyramid_oereb.contrib.interlis.interlis_2_3_utils import from_multilingual_uri_to_dict
from pyramid_oereb import Config


class DatabaseSource(BaseDatabaseSource, ThemeBaseSource):

    def from_db_to_office_record(self, offices_from_db):
        office_record = self._office_record_class(
            offices_from_db.name,
            offices_from_db.uid,
            from_multilingual_uri_to_dict(offices_from_db.multilingual_uri),
            offices_from_db.line1,
            offices_from_db.line2,
            offices_from_db.street,
            offices_from_db.number,
            offices_from_db.postal_code,
            offices_from_db.city
        )

        return office_record

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
                title=from_multilingual_text_to_dict(
                        de=document.title_de,
                        fr=document.title_fr,
                        it=document.title_it,
                        rm=document.title_rm,
                        en=document.title_en),
                responsible_office=office_record,
                published_from=document.published_from,
                published_until=document.published_until,
                text_at_web=from_multilingual_uri_to_dict(document.multilingual_uri),
                abbreviation=from_multilingual_text_to_dict(
                        de=document.abbreviation_de,
                        fr=document.abbreviation_fr,
                        it=document.abbreviation_it,
                        rm=document.abbreviation_rm,
                        en=document.abbreviation_en),
                official_number=from_multilingual_text_to_dict(
                        de=document.official_number_de,
                        fr=document.official_number_fr,
                        it=document.official_number_it,
                        rm=document.official_number_rm,
                        en=document.official_number_en),
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
            if len(legal_provision.article_numbers) == 0:
                article_numbers.append(None)
            else:
                article_nrs = []
                for article_number in legal_provision.article_numbers:
                    article_nrs.append(article_number.value)
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
                    from_multilingual_text_to_dict(
                        de=result.title_de,
                        fr=result.title_fr,
                        it=result.title_it,
                        rm=result.title_rm,
                        en=result.title_en),
                    result.extract_index,
                    results.sub_code,
                    self.get_document_records(result)
                ))
        finally:
            session.close()
