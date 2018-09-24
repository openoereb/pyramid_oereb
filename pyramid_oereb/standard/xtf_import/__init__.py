# -*- coding: utf-8 -*-
import codecs
import math
import os
import shutil
import zipfile
from datetime import datetime
from uuid import uuid4

import requests
import yaml
import logging

from defusedxml.ElementTree import parse
from pyramid.path import DottedNameResolver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from pyramid_oereb.standard.xtf_import.article import Article
from pyramid_oereb.standard.xtf_import.base_refinement import BaseRefinement
from pyramid_oereb.standard.xtf_import.document import Document
from pyramid_oereb.standard.xtf_import.document_reference import DocumentReference
from pyramid_oereb.standard.xtf_import.document_reference_definition import DocumentReferenceDefinition
from pyramid_oereb.standard.xtf_import.geometry import Geometry
from pyramid_oereb.standard.xtf_import.legend_entry import LegendEntry
from pyramid_oereb.standard.xtf_import.office import Office
from pyramid_oereb.standard.xtf_import.public_law_restriction import PublicLawRestriction
from pyramid_oereb.standard.xtf_import.public_law_restriction_document import PublicLawRestrictionDocument
from pyramid_oereb.standard.xtf_import.reference_definition import ReferenceDefinition
from pyramid_oereb.standard.xtf_import.util import get_tag
from pyramid_oereb.standard.xtf_import.view_service import ViewService


class FederalTopic(object):
    """
    Download and import data for a specified federal topic.
    """

    TAG_DATASECTION = 'DATASECTION'
    TAG_TRANSFER_STRUCTURE = 'OeREBKRMtrsfr_V1_1.Transferstruktur'
    TAG_REFERENCED_LAWS = 'OeREBKRMvs_V1_1.HinweiseGesetzlicheGrundlagen'
    TAG_OFFICE = 'OeREBKRMvs_V1_1.Vorschriften.Amt'
    TAG_DOCUMENT = 'OeREBKRMvs_V1_1.Vorschriften.Dokument'
    TAG_LEGAL_PROVISION = 'OeREBKRMvs_V1_1.Vorschriften.Rechtsvorschrift'
    TAG_ARTICLE = 'OeREBKRMvs_V1_1.Vorschriften.Artikel'
    TAG_VIEW_SERVICE = 'OeREBKRMtrsfr_V1_1.Transferstruktur.DarstellungsDienst'
    TAG_PLR = 'OeREBKRMtrsfr_V1_1.Transferstruktur.Eigentumsbeschraenkung'
    TAG_GEOMETRY = 'OeREBKRMtrsfr_V1_1.Transferstruktur.Geometrie'
    TAG_DOCUMENT_REFERENCE = 'OeREBKRMvs_V1_1.Vorschriften.HinweisWeitereDokumente'
    TAG_PUBLIC_LAW_RESTRICTION_DOCUMENT = 'OeREBKRMtrsfr_V1_1.Transferstruktur.HinweisVorschrift'
    TAG_REFERENCE_DEFINITION = 'OeREBKRMtrsfr_V1_1.Transferstruktur.HinweisDefinition'
    TAG_DOCUMENT_REFERENCE_DEFINITION = 'OeREBKRMtrsfr_V1_1.Transferstruktur.HinweisDefinitionDokument'
    TAG_BASE_REFINEMENT = 'OeREBKRMtrsfr_V1_1.Transferstruktur.GrundlageVerfeinerung'

    def __init__(self, configuration_file, topic_code, section='pyramid_oereb', arc_max_diff=0.001,
                 arc_precision=3, tmp_dir='.', srid=None):
        """

        Args:
            configuration_file (str): Path to the configuration file to be used.
            topic_code (str): The code of the federal topic to be updated.
            section (str): The section within the configuration file. (default: 'pyramid_oereb')
            arc_max_diff (float): Maximum difference between arc and line segment for stroking.
                (default: 0.001)
            arc_precision (int): Coordinate precision for generated arc points. (default: 3)
            tmp_dir (str): Directory used as temporary working directory. (default: '.')
        """
        self._log = logging.getLogger('import_federal_topic')
        with codecs.open(configuration_file, 'r', encoding='utf-8') as f:
            self._settings = yaml.safe_load(f.read()).get(section)
        topic_settings = None
        for topic in self._settings.get('plrs'):
            if topic.get('code') == topic_code:
                topic_settings = topic
        if topic_settings is None:
            self._log.error('Cannot find topic {0} in {1}'.format(topic_code, configuration_file))
            exit(1)
        self._srid = srid or self._settings.get('srid')
        if self._srid is None:
            self._log.error('No SRID defined in configuration or passed as argument')
            exit(1)
        self._tmp_dir = tmp_dir
        self._arc_max_diff = arc_max_diff
        self._arc_precision = arc_precision
        self._topic_settings = topic_settings
        self._connection = topic_settings.get('source').get('params').get('db_connection')
        models_path = topic_settings.get('source').get('params').get('models')
        self._models = DottedNameResolver().maybe_resolve(models_path)
        self._file_id = '{0}'.format(uuid4())
        self._checksum = None
        self._data_integration_office_id = None

    def load(self, xtf_files, force=False):
        """
        Updates the data for a certain federal topic.

        Args:
            xtf_files (list of str): Files to be parsed. The first one should be the XML file containing the
                federal laws, the second one the XTF file with the PLR data.
            force (bool): Set to `True` to ignore the result of the checksum comparison and update the data
                anyway.
        """

        engine = create_engine(self._connection)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            if force or self._compare_checksum(session):
                self._log.info('Starting import of topic {0}'.format(self._topic_settings.get('code')))
                self._log.info('Using SRID: {0}'.format(self._srid))
                self._log.info('Maximum difference for arc points: {0}'.format(self._arc_max_diff))
                self._log.info('Arc point coordinate precision: {0}'.format(self._arc_precision))

                self._truncate_schema(session)
                topic_source = None
                for xtf_file in xtf_files:
                    if xtf_file.endswith('.xtf'):
                        topic_source = os.path.basename(xtf_file)
                    self._log.info('Parsing {0}'.format(xtf_file))
                    content = parse(xtf_file)
                    for element in content.getroot():
                        if get_tag(element) == self.TAG_DATASECTION:
                            self._parse_datasection(session, element)

                self._update_data_integration(session, topic_source)

                self._log.info('Committing import')
                session.commit()

                self._log.info('Finished import of topic {0}'.format(self._topic_settings.get('code')))

        except Exception:
            session.rollback()
            self._log.exception('An error occurred during the import:')
            self.cleanup_files()
            exit(1)

        finally:
            session.close()

    def _compare_checksum(self, session):
        """
        Compares the checksums within the downloaded data and the database. Returns `False` if the checksums
        match or no checksum is available within the downloaded data. If the checksums are different or no
        checksum is available in the database, `True` is returned.

        Args:
            session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database interaction.

        Returns:
            bool: `True` if the data should be updated, `False` otherwise.
        """
        if self._checksum is None:
            self._log.info('No checksum available for comparison. Skipping import of data. Use "--force" to '
                           'import data anyway.')
            return False
        data_integration = session.query(self._models.DataIntegration).first()
        if data_integration is None:
            return True
        elif getattr(data_integration, 'checksum') == self._checksum:
            self._log.info('Checksums in data and database are identical. Skipping import.')
            return False
        else:
            self._log.info('Checksum in data has changed: {0} -> {1}'.format(
                getattr(data_integration, 'checksum'),
                self._checksum
            ))
            return True

    def _truncate_schema(self, session):
        """
        Truncates the tables for the specified topic.

        Args:
            session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database interaction.
        """
        models = [
            self._models.Office,
            self._models.DataIntegration,
            self._models.ReferenceDefinition,
            self._models.DocumentBase,
            self._models.Document,
            self._models.Article,
            self._models.ViewService,
            self._models.LegendEntry,
            self._models.PublicLawRestriction,
            self._models.Geometry,
            self._models.PublicLawRestrictionBase,
            self._models.PublicLawRestrictionRefinement,
            self._models.PublicLawRestrictionDocument,
            self._models.DocumentReference,
            self._models.DocumentReferenceDefinition
        ]
        self._log.info('Truncating tables:')
        for model in models:
            self._log.info('    {0}.{1}'.format(model.__table__.schema, model.__table__.name))
            session.execute('TRUNCATE {schema}.{table} CASCADE;'.format(
                schema=model.__table__.schema,
                table=model.__table__.name
            ))

    def _update_data_integration(self, session, topic_source):
        """
        Update the table `data_integration` with the data of the current import.

        Args:
            session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database interaction.
            topic_source (str): Name of the parsed XTF file.
        """
        instance = self._models.DataIntegration(
            id=topic_source,
            date=datetime.now().isoformat(),
            office_id=self._data_integration_office_id,
            checksum=self._checksum
        )
        session.add(instance)

    def _parse_datasection(self, session, datasection):
        """
        Parses the data section

        Args:
            session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database interaction.
            datasection (lxml.etree.Element): The data section element.
        """
        for element in datasection:
            tag = get_tag(element)
            if tag in [self.TAG_TRANSFER_STRUCTURE, self.TAG_REFERENCED_LAWS]:
                laws = (tag == self.TAG_REFERENCED_LAWS)
                self._parse_transfer_structure(session, element, laws=laws)

    def _parse_transfer_structure(self, session, transfer_structure, laws=False):
        """
        Parses the transfer structure content.

        Args:
            session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database interaction.
            transfer_structure (lxml.etree.Element): The transfer structure element.
            laws (bool): True if the parsed file is the XML containing the federal laws.
        """

        office = Office(session, self._models.Office)
        document = Document(session, self._models.Document)
        article = Article(session, self._models.Article)
        legend_entry = LegendEntry(session, self._models.LegendEntry, self._topic_settings.get('code'))
        view_service = ViewService(session, self._models.ViewService, legend_entry)
        public_law_restriction = PublicLawRestriction(
            session,
            self._models.PublicLawRestriction,
            self._topic_settings.get('code')
        )
        geometry = Geometry(
            session,
            self._models.Geometry,
            self._topic_settings.get('geometry_type'),
            self._srid,
            arc_max_diff=self._arc_max_diff,
            arc_precision=self._arc_precision
        )
        document_reference = DocumentReference(session, self._models.DocumentReference)
        public_law_restriction_document = PublicLawRestrictionDocument(
            session,
            self._models.PublicLawRestrictionDocument
        )
        reference_definition = ReferenceDefinition(
            session,
            self._models.ReferenceDefinition,
            self._topic_settings.get('code')
        )
        document_reference_definition = DocumentReferenceDefinition(
            session,
            self._models.DocumentReferenceDefinition
        )
        base_refinement = BaseRefinement(
            session,
            self._models.PublicLawRestrictionBase,
            self._models.PublicLawRestrictionRefinement
        )

        for element in transfer_structure:
            tag = get_tag(element)
            if tag == self.TAG_OFFICE:
                # Use the last office ID for data integration
                self._data_integration_office_id = element.attrib['TID']
                office.parse(element)
            elif tag == self.TAG_DOCUMENT:
                document.parse(element, 'Law' if laws else 'Hint')
            elif tag == self.TAG_LEGAL_PROVISION:
                document.parse(element, 'LegalProvision')
            elif tag == self.TAG_ARTICLE:
                article.parse(element)
            elif tag == self.TAG_VIEW_SERVICE:
                view_service.parse(element)
            elif tag == self.TAG_PLR:
                public_law_restriction.parse(element)
            elif tag == self.TAG_GEOMETRY:
                geometry.parse(element)
            elif tag == self.TAG_DOCUMENT_REFERENCE:
                document_reference.parse(element)
            elif tag == self.TAG_PUBLIC_LAW_RESTRICTION_DOCUMENT:
                public_law_restriction_document.parse(element)
            elif tag == self.TAG_REFERENCE_DEFINITION:
                reference_definition.parse(element)
            elif tag == self.TAG_DOCUMENT_REFERENCE_DEFINITION:
                document_reference_definition.parse(element)
            elif tag == self.TAG_BASE_REFINEMENT:
                base_refinement.parse(element)
            else:
                self._log.error('NOT IMPLEMENTED: {0}'.format(get_tag(element)))

    def download_data(self):  # pragma: no cover
        """
        Downloads the federal data for the specified topic.
        """
        file_path = os.path.join(self._tmp_dir, '{0}.zip'.format(self._file_id))
        url = self._topic_settings.get('download')
        if url is None:
            self._log.error('Missing download URL in configuration')
            exit(1)
        self._log.info('Downloading data from {0}'.format(url))
        response = requests.get(url, stream=True, proxies=self._settings.get('proxies'))
        if response.status_code < 400:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            wrote = 0
            self._log.info('Saving file to {0}'.format(file_path))
            with open(file_path, 'wb') as handle:
                for data in tqdm(
                        response.iter_content(block_size),
                        total=math.ceil(total_size//block_size),
                        unit='KB',
                        unit_scale=True
                ):
                    wrote = wrote + len(data)
                    handle.write(data)
        else:
            self._log.error('HTTP {0} - {1}'.format(response.status_code, response.content))

    def unzip_data(self):
        """
        Extracts the downloaded data into a temporary directory.
        """
        file_path = os.path.join(self._tmp_dir, '{0}.zip'.format(self._file_id))
        zip_path = os.path.join(self._tmp_dir, '{0}'.format(self._file_id))
        self._log.info('Extracting {0} to {1}'.format(file_path, zip_path))
        with open(file_path, 'rb') as f:
            zip_file = zipfile.ZipFile(f)
            for member in zip_file.namelist():
                if member.endswith('.xtf') or member.endswith('.md5.txt') \
                        or (member.endswith('.xml') and member.find('Gesetze') > -1):
                    self._log.info('\t{0}'.format(member))
                    zip_file.extract(member, zip_path)
        self._log.info('Deleting {0}'.format(file_path))
        os.remove(file_path)

    def collect_files(self):
        """
        Collects the extracted files for the data import.
        """
        path = os.path.join(self._tmp_dir, '{0}'.format(self._file_id))
        law_source = topic_source = None
        for item in os.listdir(path):
            candidate = os.path.join(path, item)
            if os.path.isfile(candidate):
                if candidate.endswith('.xtf'):
                    topic_source = candidate
                elif candidate.endswith('.xml') and candidate.find('Gesetze') > -1:
                    law_source = candidate
        files = list()
        if law_source is not None:
            self._log.info('Found law source file: {0}'.format(law_source))
            files.append(law_source)
        if topic_source is not None:
            self._log.info('Found topic source file: {0}'.format(topic_source))
            files.append(topic_source)
        return files

    def cleanup_files(self):
        """
        Removes the temporary files and directory.
        """
        path = os.path.join(self._tmp_dir, '{0}'.format(self._file_id))
        zip_file = os.path.join(self._tmp_dir, '{0}.zip'.format(self._file_id))
        if os.path.isfile(zip_file):
            self._log.info('Deleting file {0}'.format(zip_file))
            os.remove(zip_file)
        if os.path.isdir(path):
            self._log.info('Deleting folder {0}'.format(path))
            shutil.rmtree(path)

    def read_checksum(self):
        """
        Reads the data's checksum from the extracted files.
        """
        path = os.path.join(self._tmp_dir, '{0}'.format(self._file_id))
        for item in os.listdir(path):
            candidate = os.path.join(path, item)
            if os.path.isfile(candidate):
                if candidate.endswith('.md5.txt'):
                    with open(candidate, 'r') as f:
                        self._checksum = '{0}'.format(f.read()).strip()
        self._log.info('Current checksum: {0}'.format(self._checksum))
