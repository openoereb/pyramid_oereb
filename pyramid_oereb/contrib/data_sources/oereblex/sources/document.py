# -*- coding: utf-8 -*-
import logging

import datetime
from pyramid_oereb.core.config import Config
from geolink_formatter import XML
from requests.auth import HTTPBasicAuth

from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.sources import Base


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
            version (str): The used geoLink schema version. Default is 1.2.2
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
            url_param_config (list of code and url_param): Optional url parameters to use, per plr code
            code (str): The official code. Regarding to the federal specifications.
            use_prepubs (bool): If true and the law status is not "inForce", the prepubs URL will be
                used. Default is false.

        """
        super(OEREBlexSource, self).__init__()

        # Get keyword arguments
        self._version = kwargs.get('version')
        self._pass_version = kwargs.get('pass_version')
        self._mapping = kwargs.get('mapping')
        self._related_decree_as_main = kwargs.get('related_decree_as_main')
        self._related_notice_as_main = kwargs.get('related_notice_as_main')
        self._proxies = kwargs.get('proxy')
        self._code = kwargs.get('code')
        self._use_prepubs = kwargs.get('use_prepubs')

        log.debug('Use prepubs: {0}'.format(self._use_prepubs))

        # Set default values for missing parameters
        if self._version is None:
            self._version = '1.2.2'
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

        self._url_param_config = kwargs.get('url_param_config')
        if self._url_param_config:
            if not (isinstance(self._url_param_config, list)):
                raise AssertionError('url_param_config is of wrong type {}, should be list'
                                     .format(type(self._url_param_config)))
            for list_entry in self._url_param_config:
                if not (isinstance(list_entry, dict)):
                    raise AssertionError('url_param_config list entry is of wrong type {},'
                                         ' should be dictionary'.format(type(list_entry)))

    def read(self, params, geolink_id, law_status, oereblex_params=None):
        """
        Requests the geoLink for the specified ID and returns records for the received documents.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            geolink_id (int): The geoLink ID.
            law_status (pyramid_oereb.core.records.lawstatus.LawStatusRecord): The restriction's law status.
            oereblex_params (string or None): Any additional parameters to pass to Oereblex
        """
        log.debug("read() start for geolink_id {}, oereblex_params {}".format(geolink_id, oereblex_params))

        if self._use_prepubs and law_status.code != 'inForce':
            service = 'prepubs'
        else:
            service = 'geolinks'

        url_base = '{host}/api/{version}{service}/{id}.xml'
        if oereblex_params:
            url_base = url_base + '?' + oereblex_params

        # Request documents
        url = url_base.format(
            host=self._parser.host_url,
            version=self._version + '/' if self._pass_version else '',
            service=service,
            id=geolink_id,
            url_params=oereblex_params
        )

        language = params.language or self._language
        request_params = {
            'locale': language
        }
        log.debug("read() getting documents, url: {}, parser: {}".format(url, self._parser))
        documents = self._parser.from_url(url, request_params, proxies=self._proxies, auth=self._auth)
        log.debug("read() got documents")

        # Convert to records
        self.records = []
        for document in documents:
            self.records.extend(self._get_document_records(document, language))
        log.debug("read() done.")

    def _get_document_records(self, document, language):
        """
        Converts the received documents into records.

        Args:
            document (geolink_formatter.entity.Document): The geoLink document to be returned as document
                record.
            language (str): The language of the returned documents.

        Returns:
            list of pyramid_oereb.core.records.documents.DocumentRecord: The converted record.
        """

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

        # Cancel if enactment_date is not set
        if enactment_date is None:
            log.warning('Document with OEREBlex ID {0} has been skipped because of missing enactment_date.'
                        .format(document.id))
            return []

        # Check mandatory attributes
        if document.title is None:
            raise AssertionError('Missing title for document #{0}'.format(document.id))
        if authority is None:
            raise AssertionError('Missing authority for document #{0}'.format(document.id))

        # Get document type
        document_type = Config.get_document_type_by_data_code(self._code, document.doctype)

        # Create related office record
        office = OfficeRecord({language: authority}, office_at_web=document.authority_url)

        # Get files
        records = []
        for f in document.files:
            arguments = {
                'document_type': document_type,
                'index': document.index,
                'law_status': Config.get_law_status_by_data_code(self._code, u'inKraft'),
                'title': self._get_document_title(document, f, language),
                'responsible_office': office,
                'published_from': enactment_date,  # TODO: Use "publication_date" instead?
                'published_until': None,  # TODO: Use "abrogation_date"?
                'text_at_web': self._get_multilingual(f.href, language),
                'abbreviation': self._get_multilingual(document.abbreviation, language),
                'official_number': self._get_multilingual(document.number, language),
                'only_in_municipality': None,  # TODO: Use "municipality" from OEREBlex?
                'article_numbers': None
            }
            records.append(DocumentRecord(**arguments))

        return records

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
        return OEREBlexSource._get_multilingual(current_file.title or document.title, language)

    def _get_mapped_value(self, document, key, language=None):
        """
        Return the value of a mapped optional attribute.

        Args:
            document (geolink_formatter.entity.Document): The document entity.
            key (str): The key of the attribute to be mapped.
            language (str or None): Pass language to wrap value in multilingual dictionary.

        Returns:
            str or None: The value of the mapped attribute.

        TODO: Maybe obsolete?
        """
        if self._mapping:
            attribute = self._mapping.get(key)
            if attribute:
                value = getattr(document, attribute)
                if value:
                    return {language: value} if language else value
        return None

    @staticmethod
    def _get_multilingual(value, language):
        """
        Returns the title of the document/file. Extracting this logic allows
        easier customization of the file title.

        Args:
            value (str): The attribute value.
            language (str): The language of the attribute value.

        Returns:
            dict: The multilingual element.
        """

        # Skip for None values
        if value is None:
            return None

        # Assign multilingual values
        return {language: value}
