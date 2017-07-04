# -*- coding: utf-8 -*-
from geolink_formatter import XML

from pyramid_oereb.lib.records.documents import LegalProvisionRecord, DocumentRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.sources import Base


class OEREBlexSource(Base):
    def __init__(self, **kwargs):
        """
        Creates a new OEREBlex document source.

        Keyword Args:
            host (uri): Host URL of OEREBlex (without /api/...).
            language (str): The language of the received data.
            canton (str): Canton code used for the documents.
            mapping (dict of str): Mapping for optional attributes.
            proxy (dict of uri): Optional proxy configuration for HTTP and/or HTTPS.
        """
        super(OEREBlexSource, self).__init__()

        self._language = str(kwargs.get('language')).lower()
        assert self._language is not None and len(self._language) == 2

        self._canton = kwargs.get('canton')
        assert self._canton is not None and len(self._canton) == 2

        self._parser = XML(host_url=kwargs.get('host'))
        assert self._parser.host_url is not None

        self._mapping = kwargs.get('mapping')
        self._proxies = kwargs.get('proxy')

    def read(self, geolink_id):
        """
        Requests the geoLink for the specified ID and returns records for the received documents.

        Args:
            geolink_id (int): The geoLink ID.

        Returns:
            list of pyramid_oereb.lib.records.documents.DocumentRecord: The records of the received documents.
        """

        # Request documents
        url = '{host}/api/geolinks/{id}.xml'.format(host=self._parser.host_url, id=geolink_id)
        documents = self._parser.from_url(url, {}, proxies=self._proxies)

        # Get main documents
        main_documents = list()
        referenced_documents = list()
        for document in documents:
            if document.category == 'main':
                main_documents.append(document)
            elif document.category == 'related':
                referenced_documents.append(document)

        # Convert to records
        records = []
        for document in main_documents:
            records.append(self._get_document_record(document, referenced_documents))

        return records

    def _get_document_record(self, document, references=list()):
        """
        Converts the received documents into records.

        Args:
            document (geolink_formatter.entity.Document): The geoLink document to be returned as document
                record.
            references (list of geolink_formatter.entity.Document): Referenced geoLink documents.

        Returns:
            pyramid_oereb.lib.records.documents.DocumentRecord or
                pyramid_oereb.lib.records.documents.LegalProvisionRecord: The converted record.
        """

        # Get document type
        if document.doctype == 'decree':
            document_class = LegalProvisionRecord
        elif document.doctype == 'edict':
            document_class = DocumentRecord
        else:
            raise TypeError('Wrong doctype: expected decree or edict, got {0}'.format(document.doctype))

        # Assign multilingual values
        title = {self._language: document.title}

        # Create related office record
        office = OfficeRecord({self._language: document.authority}, office_at_web=document.authority_url)

        # Get optional values
        abbreviation = self._get_mapped_value(document, 'abbreviation', True)
        official_number = self._get_mapped_value(document, 'official_number')
        official_title = self._get_mapped_value(document, 'official_title', True)
        municipality = self._get_mapped_value(document, 'municipality')

        # Create referenced records list
        referenced_records = []

        # Get files
        text_at_web = None
        if len(document.files) > 1:
            for f in document.files:
                if f.category == 'main':
                    text_at_web = {self._language: document.files[0].href}
                else:
                    referenced_records.append(document_class(
                        law_status=LawStatusRecord(u'inForce'),
                        published_from=document.enactment_date,
                        title=title,
                        responsible_office=office,
                        text_at_web={self._language: f.href},
                        abbreviation=abbreviation,
                        official_number=official_number,
                        official_title=official_title,
                        canton=self._canton,
                        municipality=municipality
                    ))
        else:
            text_at_web = {self._language: document.files[0].href}
        assert text_at_web is not None

        # Convert referenced documents
        for reference in references:
            referenced_records.append(self._get_document_record(reference))

        record = document_class(
            law_status=LawStatusRecord(u'inForce'),
            published_from=document.enactment_date,
            title=title,
            responsible_office=office,
            text_at_web=text_at_web,
            abbreviation=abbreviation,
            official_number=official_number,
            official_title=official_title,
            canton=self._canton,
            municipality=municipality,
            references=referenced_records if len(referenced_records) > 0 else None
        )

        return record

    def _get_mapped_value(self, document, key, multilingual=False):
        """
        Return the value of a mapped optional attribute.

        Args:
            document (geolink_formatter.entity.Document): The document entity.
            key (str): The key of the attribute to be mapped.
            multilingual (bool): True to wrap value in multilingual dictionary.

        Returns:
            str or None: The value of the mapped attribute.
        """
        if self._mapping:
            attribute = self._mapping.get(key)
            if attribute:
                value = getattr(document, attribute)
                if value:
                    return {self._language: value} if multilingual else value
        return None
