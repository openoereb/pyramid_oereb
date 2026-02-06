# -*- coding: utf-8 -*-
import threading
import datetime
from shapely.geometry import MultiPolygon, Polygon
from unittest.mock import MagicMock, patch

from pyramid_oereb.core.processor import Processor
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.plr import PlrRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord, LegendEntryRecord
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.core.records.municipality import MunicipalityRecord
from pyramid_oereb.core.sources.plr import PlrBaseSource
from pyramid_oereb.core.views.webservice import Parameter

# Use a barrier to synchronize threads
barrier = threading.Barrier(2)


class FakePlrSource(PlrBaseSource):
    """
    A fake PLR source that uses a barrier to ensure concurrent requests overlap
    in their critical section.
    """
    def __init__(self, **kwargs):
        super(FakePlrSource, self).__init__(**kwargs)

    def read(self, params, real_estate, bbox):
        # Synchronize: both threads must reach this point before either proceeds
        barrier.wait()

        marker = real_estate.egrid
        theme = ThemeRecord(
            code=u'Theme_' + marker,
            title={'de': u'Theme Title ' + marker},
            extract_index=1
        )
        legend_entry = LegendEntryRecord(
            ImageRecord(b'123'),
            {'de': u'Legend ' + marker},
            u'Code_' + marker,
            u'TypeCodeList',
            theme
        )
        law_status = LawStatusRecord(u'inForce', {'de': u'In Force'})
        office = OfficeRecord({'de': u'Office ' + marker})
        doc_type = DocumentTypeRecord(u'Law', {'de': u'Law'})
        document = DocumentRecord(
            doc_type,
            1,
            law_status,
            {'de': u'Marker_' + marker},
            office,
            datetime.date(2020, 1, 1)
        )

        # ViewServiceRecord expects reference_wms to be a dict
        view_service = ViewServiceRecord(
            {'de': u'http://wms?marker=' + marker},
            1, 1.0, u'de', 2056
        )

        geometry = GeometryRecord(
            law_status,
            datetime.date(2020, 1, 1),
            None,
            Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        )

        plr = PlrRecord(
            theme,
            legend_entry,
            law_status,
            datetime.date(2020, 1, 1),
            None,
            office,
            ImageRecord(b'123'),
            view_service,
            [geometry],
            documents=[document]
        )
        return [plr]


def test_concurrent_requests_no_mixing():
    """
    Regression test to ensure that concurrent requests do not mix results.

    This test runs two concurrent requests (threads) that build extracts for two different
    parcels (identified by EGRID). It uses a threading.Barrier inside the PLR source's
    read method to ensure that both threads are in the "critical section" at the same time.

    The test asserts that the resulting extracts are not mixed:
    - Extract for EGRID_A must only contain results with Marker_EGRID_A.
    - Extract for EGRID_B must only contain results with Marker_EGRID_B.
    """
    barrier.reset()

    # Mocking Config to avoid external dependencies and complex initialization
    with patch('pyramid_oereb.core.readers.extract.Config') as mock_extract_config, \
         patch('pyramid_oereb.core.processor.Config') as mock_processor_config:

        # Configure mocks to return sensible values for various record initializations
        for mock_config in [mock_extract_config, mock_processor_config]:
            mock_config.get_bbox.side_effect = lambda geom: (0, 0, 10, 10)
            mock_config.get_law_status_codes.return_value = [u'inForce']
            mock_config.get_theme_by_code_sub_code.side_effect = \
                lambda code, sub_code=None: ThemeRecord(code, {'de': code}, 1)
            mock_config.get_oereb_logo.return_value = ImageRecord(b'1')
            mock_config.get_conferderation_logo.return_value = ImageRecord(b'1')
            mock_config.get_canton_logo.return_value = ImageRecord(b'1')
            mock_config.get_municipality_logo.return_value = ImageRecord(b'1')
            mock_config.get_general_information.return_value = []
            mock_config.get_map_size.return_value = (495, 280)
            mock_config.disclaimers = []
            mock_config.glossaries = []
            # We need to return a dict for various Config keys
            mock_config.get.side_effect = lambda key, default=None: {
                'default_language': u'de',
                'extract': {
                    'base_data': {'methods': {'date': 'tests.core.test_processor_concurrency.mock_date'}}
                },
                'geometry_types': {
                    'line': {'types': ['LineString', 'MultiLineString']},
                    'point': {'types': ['Point', 'MultiPoint']},
                    'polygon': {'types': ['Polygon', 'MultiPolygon']}
                }
            }.get(key, default)

        # Mock date method used in ExtractReader
        import tests.core.test_processor_concurrency
        tests.core.test_processor_concurrency.mock_date = lambda re: datetime.datetime.now()

        # Shared source and processor as in production
        shared_source = FakePlrSource(code=u'Theme_Shared')

        from pyramid_oereb.core.readers.extract import ExtractReader
        plr_cadastre_authority = OfficeRecord({'de': u'Authority'})

        processor = Processor(
            real_estate_reader=MagicMock(),
            plr_sources=[shared_source],
            extract_reader=ExtractReader([shared_source], plr_cadastre_authority)
        )

        # Prepare two distinct real estates and parameters
        re_a = RealEstateRecord(u'Type', u'Canton', u'Muni', 1234, 100,
                                MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]), egrid=u'EGRID_A')
        re_a.set_view_service(ViewServiceRecord({'de': u'http://wms'}, 1, 1.0, u'de', 2056))
        re_a.set_main_page_view_service(ViewServiceRecord({'de': u'http://wms'}, 1, 1.0, u'de', 2056))
        params_a = Parameter('json', egrid=u'EGRID_A')

        re_b = RealEstateRecord(u'Type', u'Canton', u'Muni', 1234, 100,
                                MultiPolygon([Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])]), egrid=u'EGRID_B')
        re_b.set_view_service(ViewServiceRecord({'de': u'http://wms'}, 1, 1.0, u'de', 2056))
        re_b.set_main_page_view_service(ViewServiceRecord({'de': u'http://wms'}, 1, 1.0, u'de', 2056))
        params_b = Parameter('json', egrid=u'EGRID_B')

        muni = MunicipalityRecord(1234, u'Muni', True)

        results = {}

        def run_proc(name, re, params):
            try:
                # Each thread needs to see the municipality as published
                with patch('pyramid_oereb.core.processor.Config.municipality_by_fosnr', return_value=muni):
                    extract = processor.process(re, params, u'http://test.ch')
                    results[name] = extract
            except Exception as e:
                results[name] = e

        t1 = threading.Thread(target=run_proc, args=('A', re_a, params_a))
        t2 = threading.Thread(target=run_proc, args=('B', re_b, params_b))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        extract_a = results['A']
        extract_b = results['B']

        # Ensure no exceptions occurred
        if isinstance(extract_a, Exception):
            raise extract_a
        if isinstance(extract_b, Exception):
            raise extract_b

        # Verify results for Request A
        assert extract_a.real_estate.egrid == u'EGRID_A'
        assert len(extract_a.real_estate.public_law_restrictions) > 0
        for plr in extract_a.real_estate.public_law_restrictions:
            # Check that the PLR belongs to EGRID_A and NOT EGRID_B
            assert plr.documents[0].title['de'] == u'Marker_EGRID_A'
            assert plr.theme.code == u'Theme_EGRID_A'

        # Verify results for Request B
        assert extract_b.real_estate.egrid == u'EGRID_B'
        assert len(extract_b.real_estate.public_law_restrictions) > 0
        for plr in extract_b.real_estate.public_law_restrictions:
            # Check that the PLR belongs to EGRID_B and NOT EGRID_A
            assert plr.documents[0].title['de'] == u'Marker_EGRID_B'
            assert plr.theme.code == u'Theme_EGRID_B'
