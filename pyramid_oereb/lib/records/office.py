# -*- coding: utf-8 -*-
import warnings


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

        Args:
            name (dict):  The official name of the authority (multilingual)
            uid (str): The unique identifier of the authority in the federal register
            office_at_web (str): The URL to the office's homepage
            line1 (str): Complementary address information
            line2 (str): Complementary address information
            street (str): The street where the authority is located
            number (str): House number
            postal_code (integer): ZIP Code of the
            postal_code (str): The city where the authority is located
        """
        if not isinstance(name, dict):
            warnings.warn('Type of "name" should be "dict"')

        self.name = name
        self.uid = uid
        self.office_at_web = office_at_web
        self.line1 = line1
        self.line2 = line2
        self.street = street
        self.number = number
        self.postal_code = postal_code
        self.city = city
