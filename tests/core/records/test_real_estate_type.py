from pyramid_oereb.core.records.real_estate_type import RealEstateTypeRecord


def test_real_estate_type_init():
    record = RealEstateTypeRecord(u'code', {u'de': u'Liegenschaft'})
    assert record.code == u'code'
    assert record.title == {u'de': u'Liegenschaft'}
