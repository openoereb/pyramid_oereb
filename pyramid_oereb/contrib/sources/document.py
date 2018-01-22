# -*- coding: utf-8 -*-
import logging

from geolink_formatter import XML
from requests.auth import HTTPBasicAuth

from pyramid_oereb.lib.records.documents import LegalProvisionRecord, DocumentRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.sources import Base


log = logging.getLogger(__name__)


class OEREBlexSource(Base):
    """
    A document source, that creates records for the received documents from OEREBlex for the specified
    geoLink.
    """
    def __init__(self, **kwargs):
        """
        Creates a new OEREBlex document source.

        Keyword Args:
            host (uri): Host URL of OEREBlex (without /api/...).
            version (str): The used geoLink schema version. Default is 1.1.0
            pass_version (bool): True to pass version in URL, false otherwise. Defaults is false.
            language (str): The language of the received data.
            canton (str): Canton code used for the documents.
            mapping (dict of str): Mapping for optional attributes.
            related_decree_as_main (bool): Add related decrees directly to the public law restriction.
            proxy (dict of uri): Optional proxy configuration for HTTP and/or HTTPS.
            auth (dict of str): Optional credentials for basic authentication. Requires `username`
                and `password` to be defined.

        """
        super(OEREBlexSource, self).__init__()

        # Get keyword arguments
        self._version = kwargs.get('version')
        self._pass_version = kwargs.get('pass_version')
        self._mapping = kwargs.get('mapping')
        self._related_decree_as_main = kwargs.get('related_decree_as_main')
        self._proxies = kwargs.get('proxy')

        # Set default values for missing parameters
        if self._version is None:
            self._version = '1.1.0'
        if self._pass_version is None:
            self._pass_version = False

        auth = kwargs.get('auth')
        if isinstance(auth, dict) and 'username' in auth and 'password' in auth:
            self._auth = HTTPBasicAuth(auth.get('username'), auth.get('password'))
        else:
            self._auth = None

        self._language = str(kwargs.get('language')).lower()
        assert self._language is not None and len(self._language) == 2

        self._canton = kwargs.get('canton')
        assert self._canton is not None and len(self._canton) == 2

        self._parser = XML(host_url=kwargs.get('host'), version=self._version)
        assert self._parser.host_url is not None

    def read(self, geolink_id):
        """
        Requests the geoLink for the specified ID and returns records for the received documents.

        Args:
            geolink_id (int): The geoLink ID.
        """
        log.debug("read() start")

        # Request documents
        url = '{host}/api/{version}geolinks/{id}.xml'.format(
            host=self._parser.host_url,
            version=self._version + '/' if self._pass_version else '',
            id=geolink_id
        )
        log.debug("read() getting documents, url: {}, parser: {}".format(url, self._parser))
        documents = self._parser.from_url(url, {}, proxies=self._proxies, auth=self._auth)
        log.debug("read() got documents")

        # Get main documents
        main_documents = list()
        referenced_documents = list()
        for document in documents:
            if document.category == 'main':
                main_documents.append(document)
            elif document.category == 'related' and document.doctype == 'decree' \
                    and self._related_decree_as_main:
                main_documents.append(document)
            else:
                referenced_documents.append(document)

        # Convert to records
        self.records = []
        for document in main_documents:
            self.records.extend(self._get_document_records(document, referenced_documents))
        log.debug("read() done.")

    def _get_document_records(self, document, references=list()):
        """
        Converts the received documents into records.

        Args:
            document (geolink_formatter.entity.Document): The geoLink document to be returned as document
                record.
            references (list of geolink_formatter.entity.Document): Referenced geoLink documents.

        Returns:
            list of pyramid_oereb.lib.records.documents.DocumentRecord: The converted record.
        """

        # Cancel if document contains no files
        if len(document.files) == 0:
            log.warning('Document with OEREBlex ID {0} has been skipped because of missing file.'.format(
                document.id
            ))
            return []

        # Check mandatory attributes
        assert document.title is not None
        assert document.enactment_date is not None
        assert document.authority is not None

        # Get document type
        if document.doctype == 'decree':
            document_class = LegalProvisionRecord
        elif document.doctype == 'edict':
            document_class = DocumentRecord
        else:
            raise TypeError('Wrong doctype: expected decree or edict, got {0}'.format(document.doctype))

        # Convert referenced documents
        referenced_records = []
        for reference in references:
            referenced_records.extend(self._get_document_records(reference))

        # Assign multilingual values
        title = {self._language: document.title}

        # Create related office record
        office = OfficeRecord({self._language: document.authority}, office_at_web=document.authority_url)

        # Get files
        records = []
        for f in document.files:
            records.append(document_class(
                law_status=LawStatusRecord.from_config(u'inForce'),
                published_from=document.enactment_date,
                title=title,
                responsible_office=office,
                text_at_web={self._language: f.href},
                abbreviation=document.abbreviation,
                official_number=document.number,
                official_title=self._get_mapped_value(document, 'official_title', True),
                canton=self._canton,
                municipality=self._get_mapped_value(document, 'municipality'),
                references=referenced_records if len(referenced_records) > 0 else None
            ))

        return records

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
