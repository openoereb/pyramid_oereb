# -*- coding: utf-8 -*-


class AuthorityRecord(object):
    uid = None
    name = None
    office_at_web = None
    line1 = None
    line2 = None
    street = None
    number = None
    postal_code = None
    city = None

    def __init__(self, uid = None, name = None, office_at_web = None, line1 = None, line2 = None, 
        street = None, number = None, postal_code = None, city = None):
        """
        Competent authority record.
        :param uid:             The unique identifier of the authority in the federal register
        :type  uid:             str
        :param name:               The official name of the authority
        :type  name:               str
        :param office_at_web:               The URL to the office's homepage
        :type office_at_web:               str
        :param line1:               Complementary address information
        :type line1:               str
        :param line2:               Complementary address information
        :type line2:               str
        :param street:               The street where the authority is located
        :type street:               str
        :param number:               House number
        :type number:               str
        :param postal_code:               ZIP Code of the 
        :type postal_code:               integer
        :param city:               The city where the authority is located
        :type postal_code:               str
        """

        if not (uid and name):
            raise TypeError('Fields "uid" and "name" must be defined. '
                            'Got {0}, {1}.'.format(uid, name))

        self.uid = uid
        self.name = name
        self.office_at_web = office_at_web
        self.line1 = line1
        self.line2 = line2
        self.street = street
        self.number = type_code
        self.postal_code = type_code_list
        self.city = view_service
        self.basis = basis

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return:    List of available field names.
        :rtype:     list
        """
        return [
            'uid',
            'name',
            'office_at_web',
            'line1',
            'line2',
            'street',
            'number',
            'postal_code',
            'city'
        ]
