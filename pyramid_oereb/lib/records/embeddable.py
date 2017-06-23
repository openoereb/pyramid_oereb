# -*- coding: utf-8 -*-


class EmbeddableRecord(object):

    def __init__(self, cadaster_state, cadaster_organisation, data_owner_cadastral_surveying,
                 transfer_from_source_cadastral_surveying, themes):
        """
        The record for handling the address entity inside the application.

        Args:
            cadaster_state (datetime.datetime): Actuality of the oereb cadaster.
            cadaster_organisation (pyramid_oereb.lib.records.office.OfficeRecord): The information of the
                organisation which provides this cadaster.
            data_owner_cadastral_surveying (pyramid_oereb.lib.records.office.OfficeRecord): The information
                about the office which povides the surveying data for this extract.
            transfer_from_source_cadastral_surveying (datetime.datetime): The actuality of the surveying data
                used for this extract.
            themes (list of pyramid_oereb.lib.records.theme.Theme): All the theme information on the
                extract
        """

        # TODO: there is a element called pdf inside the OREB-XML-Aufruf specification in the embeddable
        # section which is realy mystic, it is documented nowhere!!!
        self.cadaster_state = cadaster_state
        self.cadaster_organisation = cadaster_organisation
        self.data_owner_cadastral_surveying = data_owner_cadastral_surveying
        self.transfer_from_source_cadastral_surveying = transfer_from_source_cadastral_surveying
        self.data_sources = themes


class TransferFromSourceRecord(object):

    def __init__(self, date, owner):
        """
        The record for handling the address entity inside the application.

        Args:
            date (datetime.datetime): Actuality of the oereb cadaster.
            owner (pyramid_oereb.lib.records.office.OfficeRecord): The information of the
                organisation which provides this cadaster.
        """
        self.date = date
        self.owner = owner
