# -*- coding: utf-8 -*-
import logging

import datetime
from geolink_formatter import XML
from requests.auth import HTTPBasicAuth

from pyramid_oereb.lib.records.documents import LegalProvisionRecord, LawRecord, HintRecord
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
            version (str): The used geoLink schema version. Default is 1.2.0
            pass_version (bool): True to pass version in URL, false otherwise. Defaults is false.
            language (str): The language of the received data.
            canton (str): Canton code used for the documents.
            mapping (dict of str): Mapping for optional attributes.
            related_decree_as_main (bool): Add related decrees directly to the public law restriction.
            related_notice_as_main (bool): Add related notices directly to the public law restriction.
            proxy (dict of uri): Optional proxy configuration for HTTP and/or HTTPS.
            auth (dict of str): Optional credentials for basic authentication. Requires `username`
                and `password` to be defined.
            validation (bool): Turn XML validation on/off. Default is true.

        """
        super(OEREBlexSource, self).__init__()

        # Get keyword arguments
        self._version = kwargs.get('version')
        self._pass_version = kwargs.get('pass_version')
        self._mapping = kwargs.get('mapping')
        self._related_decree_as_main = kwargs.get('related_decree_as_main')
        self._related_notice_as_main = kwargs.get('related_notice_as_main')
        self._proxies = kwargs.get('proxy')

        # Set default values for missing parameters
        if self._version is None:
            self._version = '1.2.0'
        if self._pass_version is None:
            self._pass_version = False

        auth = kwargs.get('auth')
        if isinstance(auth, dict) and 'username' in auth and 'password' in auth:
            self._auth = HTTPBasicAuth(auth.get('username'), auth.get('password'))
        else:
            self._auth = None

        self._language = str(kwargs.get('language')).lower()
        if not (isinstance(self._language, str) and len(self._language) == 2):
            raise AssertionError('language has to be string of two characters, e.g. "de" or "fr"')

        self._canton = kwargs.get('canton')
        if not (isinstance(self._canton, str) and len(self._canton) == 2):
            raise AssertionError('canton has to be string of two characters, e.g. "BL" or "NE"')

        if kwargs.get('validation') is not None:
            xsd_validation = kwargs.get('validation')
        else:
            xsd_validation = True
        self._parser = XML(host_url=kwargs.get('host'), version=self._version, xsd_validation=xsd_validation)
        if self._parser.host_url is None:
            raise AssertionError('host_url has to be defined')

    def read(self, params, geolink_id):
        """
        Requests the geoLink for the specified ID and returns records for the received documents.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            geolink_id (int): The geoLink ID.
        """
        log.debug("read() start")

        # Request documents
        url = '{host}/api/{version}geolinks/{id}.xml'.format(
            host=self._parser.host_url,
            version=self._version + '/' if self._pass_version else '',
            id=geolink_id
        )
        language = params.language or self._language
        request_params = {
            'locale': language
        }
        log.debug("read() getting documents, url: {}, parser: {}".format(url, self._parser))
        documents = self._parser.from_url(url, request_params, proxies=self._proxies, auth=self._auth)
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
            elif document.category == 'related' and document.doctype == 'notice' \
                    and self._related_notice_as_main:
                main_documents.append(document)
            else:
                referenced_documents.append(document)

        # Convert to records
        self.records = []
        for document in main_documents:
            self.records.extend(self._get_document_records(document, language, referenced_documents))
        log.debug("read() done.")

    def _get_document_records(self, document, language, references=None):
        """
        Converts the received documents into records.

        Args:
            document (geolink_formatter.entity.Document): The geoLink document to be returned as document
                record.
            language (str): The language of the returned documents.
            references (list of geolink_formatter.entity.Document): Referenced geoLink documents.

        Returns:
            list of pyramid_oereb.lib.records.documents.DocumentRecord: The converted record.
        """

        references = references or list()

        # Cancel if document contains no files
        if len(document.files) == 0:
            log.warning('Document with OEREBlex ID {0} has been skipped because of missing file.'.format(
                document.id
            ))
            return []

        enactment_date = document.enactment_date
        authority = document.authority
        if document.doctype == 'notice':
            # Oereblex notices documents can have no enactment_date while it is require by pyramid_oereb to
            # have one. Add a fake default one that is identifiable and always older than now (01.0.1.1970).
            if enactment_date is None:
                enactment_date = datetime.date(1970, 1, 1)
            # Oereblex notices documents can have no `authority` while it is require by pyramid_oereb to
            # have one. Replace None by '-' in this case.
            if authority is None:
                authority = '-'

        # Check mandatory attributes
        if document.title is None:
            raise AssertionError('Missing title for document #{0}'.format(document.id))
        if enactment_date is None:
            raise AssertionError('Missing enactment_date for document #{0}'.format(document.id))
        if authority is None:
            raise AssertionError('Missing authority for document #{0}'.format(document.id))

        # Get document type
        if document.doctype == 'decree':
            document_class = LegalProvisionRecord
        elif document.doctype == 'edict':
            document_class = LawRecord
        elif document.doctype == 'notice':
            document_class = HintRecord
        else:
            raise TypeError('Wrong doctype: expected decree, edict or notice, got {0}'.format(
                document.doctype
            ))

        # Convert referenced documents
        referenced_records = []
        for reference in references:
            referenced_records.extend(self._get_document_records(reference, language))

        # Create related office record
        office = OfficeRecord({language: authority}, office_at_web=document.authority_url)

        # Check for available abbreviation
        abbreviation = {language: document.abbreviation} if document.abbreviation else None

        # Get files
        records = []
        for f in document.files:
            arguments = {'law_status': LawStatusRecord.from_config(u'inForce'),
                         'published_from': enactment_date,
                         'title': self._get_document_title(document, f, language),
                         'responsible_office': office,
                         'text_at_web': {language: f.href},
                         'abbreviation': abbreviation,
                         'official_number': document.number,
                         'official_title': self._get_mapped_value(
                             document,
                             'official_title',
                             language=language
                         ),
                         'canton': self._canton,
                         'municipality': self._get_mapped_value(document, 'municipality'),
                         'references': referenced_records if len(referenced_records) > 0 else None}
            records.append(document_class(**arguments))

        return records

    def _get_mapped_value(self, document, key, language=None):
        """
        Return the value of a mapped optional attribute.

        Args:
            document (geolink_formatter.entity.Document): The document entity.
            key (str): The key of the attribute to be mapped.
            language (str or None): Pass language to wrap value in multilingual dictionary.

        Returns:
            str or None: The value of the mapped attribute.
        """
        if self._mapping:
            attribute = self._mapping.get(key)
            if attribute:
                value = getattr(document, attribute)
                if value:
                    return {language: value} if language else value
        return None

    @staticmethod
    def _get_document_title(document, current_file, language):
        """
        Returns the title of the document/file. Extracting this logic allows
        easier customization of the file title.

        Args:
            document (geolink_formatter.entity.Document): The document entity.
            current_file (geolink_formatter.entity.File): The file, which gets annotated with a title.
            language (str): The language of the document title.

        Returns:
            str: Title of document.
        """
        # Assign multilingual values
        return {language: document.title}
