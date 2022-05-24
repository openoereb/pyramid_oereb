# -*- coding: utf-8 -*-


class DataIntegrationRecord(object):

    def __init__(self, date, checksum=None, theme=None, office=None,
                 theme_identifier=None, office_identifier=None):
        """
        The record to check if data is available for municipality.

        Args:
            date (datetime.date): The date when data for the theme was delivered.
            theme (pyramid_oereb.core.records.ThemeRecord or None): The theme code
                which this element belongs to.
            office (pyramid_oereb.core.records.office.OfficeRecord or None): The office
                this element belongs to.
            checksum (str or None): A checksum to persist the data state which is in the
                db. It is thought to be a helper field to check if import is necessary.
            theme_identifier (str|int|None): The identifier which can be used to match the
                corresponding theme.
            office_identifier (str|int|None): The identifier which can be used to match the
                corresponding office.
        """
        if theme is None and theme_identifier is None:
            raise AttributeError('Either theme or theme_identifier has to be defined!')
        if office is None and office_identifier is None:
            raise AttributeError('Either office or  office_identifier has to be defined!')
        self.date = date
        self.theme = theme
        self.office = office
        self.checksum = checksum
        self.theme_identifier = theme_identifier
        self.office_identifier = office_identifier
