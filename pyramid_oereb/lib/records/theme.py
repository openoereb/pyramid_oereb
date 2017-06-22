# -*- coding: utf-8 -*-
import warnings


class ThemeRecord(object):

    def __init__(self, code, text):
        """
        Creates a new theme record.

        Args:
            code (unicode): The theme's code.
            text (dict of unicode): The multilingual description.
            data_owner (pyramid_oereb.lib.records.office.OfficeRecord):
            transfer_from_source (datetime.date): The actuality of the themes data
        """
        if not isinstance(text, dict):
            warnings.warn('Type of "text" should be "dict"')

        self.code = code
        self.text = text


class EmbeddableThemeRecord(ThemeRecord):

    def __init__(self, code, text, sources):
        """
        Creates a new theme record.

        Args:
            code (unicode): The theme's code.
            text (dict of unicode): The multilingual description.
            sources (list of pyramid_oereb.lib.records.embeddable.TransferFromSourceRecord): All the
                sources belonging to this theme.
        """
        super(EmbeddableThemeRecord, self).__init__(code, text)
        self.sources = sources
