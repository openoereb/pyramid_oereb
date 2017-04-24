# -*- coding: utf-8 -*-


class OfficeRecord(object):
    name = None
    uid = None
    office_at_web = None
    line1 = None
    line2 = None
    street = None
    number = None
    postal_code = None
    city = None

    def __init__(self, name, uid=None, office_at_web=None, line1=None, line2=None,
                 street=None, number=None, postal_code=None, city=None):
        """
        Responsible office record.
        :param name:  The official name of the authority
        :type  name: str
        :param uid: The unique identifier of the authority in the federal register
        :type  uid: str
        :param office_at_web: The URL to the office's homepage
        :type office_at_web: str
        :param line1: Complementary address information
        :type line1: str
        :param line2: Complementary address information
        :type line2: str
        :param street: The street where the authority is located
        :type street: str
        :param number: House number
        :type number: str
        :param postal_code: ZIP Code of the
        :type postal_code: integer
        :param city: The city where the authority is located
        :type postal_code: str
        """

        self.name = name
        self.uid = uid
        self.office_at_web = office_at_web
        self.line1 = line1
        self.line2 = line2
        self.street = street
        self.number = number
        self.postal_code = postal_code
        self.city = city

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return:    List of available field names.
        :rtype:     list
        """

        return [
            'name',
            'uid',
            'office_at_web',
            'line1',
            'line2',
            'street',
            'number',
            'postal_code',
            'city'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in self.get_fields():
            value = getattr(self, key)
            if value:
                extract[key] = value
        return extract
