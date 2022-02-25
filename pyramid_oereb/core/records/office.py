# -*- coding: utf-8 -*-
import warnings


class OfficeRecord(object):
    """
    Responsible office record.

    Attributes:
        name (dict of unicode):  The official name of the authority (multilingual)
        uid (unicode): The unique identifier of the authority in the federal register
        office_at_web (dict of unicode): The URL to the office's homepage (multilingual)
        line1 (unicode): Complementary address information
        line2 (unicode): Complementary address information
        street (unicode): The street where the authority is located
        number (unicode): House number
        postal_code (integer): ZIP Code of the
        city (unicode): The city where the authority is located
            identifier (str): The identifier of the theme which might be used for linking to other elements.
    """
    def __init__(self, name, uid=None, office_at_web=None, line1=None, line2=None,
                 street=None, number=None, postal_code=None, city=None, identifier=None):
        """
        Args:
            name (dict of unicode):  The official name of the authority (multilingual)
            uid (unicode): The unique identifier of the authority in the federal register
            office_at_web (dict of unicode): The URL to the office's homepage (multilingual)
            line1 (unicode): Complementary address information
            line2 (unicode): Complementary address information
            street (unicode): The street where the authority is located
            number (unicode): House number
            postal_code (integer): ZIP Code of the
            city (unicode): The city where the authority is located
                identifier (str): The identifier of the theme which might be used for linking to other
                elements.
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
        self.identifier = identifier
