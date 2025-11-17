import pytest
from unittest.mock import patch

from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from pyramid_oereb.contrib.data_sources.standard.sources.real_estate import DatabaseSource
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.views.webservice import Parameter


@pytest.fixture
def real_estate_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.RealEstate",
        "record_class": "pyramid_oereb.core.records.real_estate.RealEstateRecord"
    }


@pytest.fixture
def wkb_multipolygons():
    yield [WKTElement(
        "SRID=2056;MULTIPOLYGON((("
        "2609229.759 1263666.789,"
        "2609231.206 1263670.558,"
        "2609229.561 1263672.672,"
        "2609229.472 1263675.47,"
        "2609251.865 1263727.506,"
        "2609275.847 1263783.29,"
        "2609229.759 1263666.789"
        ")))",
        extended=True
    ), WKTElement(
        "SRID=2056;MULTIPOLYGON((("
        "2608901.529 1261990.655,"
        "2608898.665 1261991.598,"
        "2608895.798 1261992.53,"
        "2608892.928 1261993.452,"
        "2608890.054 1261994.363,"
        "2608880.256 1261996.496"
        "2608901.529 1261990.655"
        ")))",
        extended=True
    )]


@pytest.fixture
def real_estates(wkb_multipolygons):
    from pyramid_oereb.contrib.data_sources.standard.models.main import RealEstate
    yield [
        RealEstate(**{
            "id": 1,
            "fosnr": 2771,
            "limit": wkb_multipolygons[0],
            "type": "Liegenschaft",
            "canton": "BL",
            "identdn": "BL0200002771",
            "municipality": "Oberwil (BL)",
            "number": "70",
            "egrid": "CH113928077734",
            "land_registry_area": 35121,
            "subunit_of_land_register": "TEST",
            "subunit_of_land_register_designation": "TEST",
            "metadata_of_geographical_base_data": "https://testmetadata.url"
        }),
        RealEstate(**{
            "id": 2,
            "fosnr": 2771,
            "limit": wkb_multipolygons[0],
            "type": "Liegenschaft",
            "canton": "BL",
            "identdn": "BL0200002771",
            "municipality": "Oberwil (BL)",
            "number": "71",
            "egrid": "CH113928077735",
            "land_registry_area": 351,
            "subunit_of_land_register": "TEST",
            "subunit_of_land_register_designation": "TEST",
            "metadata_of_geographical_base_data": "https://testmetadata.url"
        })
    ]


@pytest.fixture
def all_real_estate_result_session(session, query, real_estates):

    class Query(query):

        def all(self):
            return real_estates

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def all_real_estate_filtered_by_geometry_session(session, query, real_estates):

    class Query(query):

        def all(self):
            return real_estates

        def filter(self, term):
            assert term == 1
            return self

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def all_real_estate_filtered_by_egrid_session(session, query, real_estates):

    class Query(query):

        def all(self):
            return [real_estates[0]]

        def filter(self, term):
            assert term.right.value == 'CH113928077734'
            return self

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def all_real_estate_filtered_by_nbident_and_number_session(session, query, real_estates):

    class Query(query):

        def all(self):
            return [real_estates[0]]

        def filter(self, term1, term2):
            assert term1.right.value == '71'
            assert term2.right.value == 1
            return self

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(real_estate_source_params, all_real_estate_result_session, wkb_multipolygons):
    source = DatabaseSource(**real_estate_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_real_estate_result_session()):  # noqa: E501
        source.read(
            Parameter('xml'),
            geometry="SRID=2056;MULTIPOLYGON(2608901.529 1261990.655,2608898.665 1261991.598)"
        )
        assert len(source.records) == 2
        assert isinstance(source.records[0], RealEstateRecord)
        assert isinstance(source.records[1], RealEstateRecord)
        record = source.records[0]
        assert record.type == 'Liegenschaft'
        assert record.canton == 'BL'
        assert record.municipality == 'Oberwil (BL)'
        assert record.fosnr == 2771
        assert record.land_registry_area == 35121
        assert record.limit.geom_type == to_shape(wkb_multipolygons[0]).geom_type
        assert record.metadata_of_geographical_base_data == "https://testmetadata.url"
        assert record.number == '70'
        assert record.identdn == "BL0200002771"
        assert record.egrid == 'CH113928077734'
        assert record.subunit_of_land_register == 'TEST'
        assert record.subunit_of_land_register_designation == 'TEST'


def test_read_all_filtered_by_egrid(real_estate_source_params, all_real_estate_filtered_by_egrid_session):
    source = DatabaseSource(**real_estate_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_real_estate_filtered_by_egrid_session()):  # noqa: E501
        source.read(Parameter('xml'), egrid='CH113928077734')
        assert len(source.records) == 1


def test_read_all_filtered_by_nbident_and_number(real_estate_source_params, all_real_estate_filtered_by_nbident_and_number_session):  # noqa: E501
    source = DatabaseSource(**real_estate_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_real_estate_filtered_by_nbident_and_number_session()):  # noqa: E501
        source.read(Parameter('xml'), nb_ident=1, number='71')
        assert len(source.records) == 1


def test_read_all_missing_param(real_estate_source_params, all_real_estate_result_session):
    source = DatabaseSource(**real_estate_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_real_estate_result_session()):  # noqa: E501
        with pytest.raises(AttributeError):
            source.read(Parameter('xml'))
