# -*- coding: utf-8 -*-
import datetime
from pyramid_oereb import Config
from pyramid.path import DottedNameResolver
from pyramid_oereb.lib.records.embeddable import EmbeddableRecord, DatasourceRecord
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.glossary import GlossaryRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from shapely.geometry import MultiPolygon, Polygon
from tests.conftest import pyramid_oereb_test_config


class DummyRenderInfo(object):
    name = 'test'


def get_test_extract():
    date = datetime.datetime.now()
    with pyramid_oereb_test_config():
        view_service = ViewServiceRecord(u'http://geowms.bl.ch',
                                         1,
                                         1.0,
                                         u'http://geowms.bl.ch',
                                         None)
        real_estate = RealEstateRecord(u'RealEstate', u'BL', u'Liestal', 2829, 11395,
                                       MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                                       u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712')
        real_estate.set_view_service(view_service)
        real_estate.set_main_page_view_service(view_service)
        office_record = OfficeRecord({'de': u'AGI'})
        resolver = DottedNameResolver()
        date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
        date_method = resolver.resolve(date_method_string)
        av_update_date = date_method(real_estate)
        base_data = Config.get_base_data(av_update_date)

        av_provider_method_string = Config.get('extract').get('base_data').get('methods').get('provider')
        av_provider_method = resolver.resolve(av_provider_method_string)
        cadaster_state = date
        theme = ThemeRecord(u'TEST', {'de': u'TEST TEXT'})
        datasources = [DatasourceRecord(theme, date, office_record)]
        plr_cadastre_authority = Config.get_plr_cadastre_authority()
        embeddable = EmbeddableRecord(
            cadaster_state,
            plr_cadastre_authority,
            av_provider_method(real_estate),
            av_update_date,
            datasources
        )
        extract = ExtractRecord(
            real_estate,
            ImageRecord('1'.encode('utf-8')),
            ImageRecord('2'.encode('utf-8')),
            ImageRecord('3'.encode('utf-8')),
            ImageRecord('4'.encode('utf-8')),
            office_record,
            base_data,
            embeddable,
            exclusions_of_liability=[
                ExclusionOfLiabilityRecord({'de': u'Haftungsausschluss'}, {'de': u'Test'})
            ],
            glossaries=[GlossaryRecord({'de': u'Glossar'}, {'de': u'Test'})],
            general_information={'de': u'Allgemeine Informationen'},
            certification={'de': u'certification'},
            certification_at_web={'de': u'certification_at_web'},
        )
        # extract.qr_code = 'VGhpcyBpcyBub3QgYSBRUiBjb2Rl'.encode('utf-8') TODO:
        #    qr_code Must be an image ('base64Binary'), but even with images xml validation
        #    fails on it.
        # extract.electronic_signature = 'Signature'  # TODO: fix signature rendering first
        return extract
