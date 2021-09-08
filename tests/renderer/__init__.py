# -*- coding: utf-8 -*-
import datetime
from pyramid_oereb import Config
from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.records.embeddable import EmbeddableRecord, DatasourceRecord
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.glossary import GlossaryRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from shapely.geometry import MultiPolygon, Polygon
from tests import pyramid_oereb_test_config


class DummyRenderInfo(object):
    name = 'test'


def get_default_extract():
    glossary = [GlossaryRecord({'de': u'Glossar'}, {'de': u'Test'})]
    return _get_test_extract(glossary)


def get_empty_glossary_extract():
    return _get_test_extract([])


def get_none_glossary_extract():
    return _get_test_extract(None)


def _get_test_extract(glossary):
    date = datetime.datetime.now()
    with pyramid_oereb_test_config():
        view_service = ViewServiceRecord({'de': u'http://geowms.bl.ch'},
                                         1,
                                         1.0,
                                         None)
        real_estate = RealEstateRecord(u'Liegenschaft', u'BL', u'Liestal', 2829, 11395,
                                       MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                                       u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712')
        real_estate.set_view_service(view_service)
        real_estate.set_main_page_view_service(view_service)
        office_record = OfficeRecord({'de': u'AGI'}, office_at_web={
            'de': 'https://www.bav.admin.ch/bav/de/home.html'
        })
        resolver = DottedNameResolver()
        date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
        date_method = resolver.resolve(date_method_string)
        update_date_os = date_method(real_estate)

        os_provider_method_string = Config.get('extract').get('base_data').get('methods').get('provider')
        os_provider_method = resolver.resolve(os_provider_method_string)
        cadaster_state = date
        theme = ThemeRecord(u'TEST', {'de': u'TEST TEXT'}, 100)
        datasources = [DatasourceRecord(theme, date, office_record)]
        plr_cadastre_authority = Config.get_plr_cadastre_authority()
        embeddable = EmbeddableRecord(
            cadaster_state,
            plr_cadastre_authority,
            os_provider_method(real_estate),
            update_date_os,
            datasources
        )
        extract = ExtractRecord(
            real_estate,
            Config.get_oereb_logo(),
            Config.get_conferderation_logo(),
            Config.get_canton_logo(),
            Config.get_municipality_logo(1234),
            office_record,
            update_date_os,
            embeddable,
            exclusions_of_liability=[
                ExclusionOfLiabilityRecord({'de': u'Haftungsausschluss'}, {'de': u'Test'})
            ],
            glossaries=glossary,
            general_information=Config.get_general_information(),
            certification={'de': u'certification'},
            certification_at_web={'de': u'certification_at_web'},
        )
        # extract.qr_code = 'VGhpcyBpcyBub3QgYSBRUiBjb2Rl'.encode('utf-8') TODO:
        #    qr_code Must be an image ('base64Binary'), but even with images xml validation
        #    fails on it.
        # extract.electronic_signature = 'Signature'  # TODO: fix signature rendering first
        return extract
