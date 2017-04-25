# -*- coding: utf-8 -*-


class GeometryRecord(object):
    legal_state = None
    published_from = None
    geo_metadata = None
    geom = None
    public_law_restriction = None
    office = None

    def __init__(
            self, legal_state, published_from, geom, geo_metadata=None, public_law_restriction=None,
            office=None):
        """
        Geometry record
        :param legal_state: The PLR record's legal state.
        :type legal_state: str
        :param published_from: Date from/since when the PLR record is published.
        :type published_from: datetime.date
        :param geom: The geometry
        :type geom: shapely.geometry.base.BaseGeometry
        :param geo_metadata: The metadata
        :type geo_metadata: str
        :param public_law_restriction: The public law restriction
        :type public_law_restriction: pyramid_oereb.lib.records.plr.PlrRecord
        :param office: The office
        :type office: pyramid_oereb.lib.records.office.Office
        """

        self.legal_state = legal_state
        self.published_from = published_from
        self.geo_metadata = geo_metadata
        self.geom = geom
        self.public_law_restriction = public_law_restriction
        self.office = office

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'legal_state',
            'published_from',
            'geo_metadata',
            'geom',
            'public_law_restriction',
            'office'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in [
            'legal_state',
            'geo_metadata',
            'geom'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value
        key = 'office'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract()
        key = 'geom'
        extract[key] = str(getattr(self, key))
        return extract
