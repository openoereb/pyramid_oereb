# -*- coding: utf-8 -*-


class EmbeddableRecord(object):

    def __init__(self, cadaster_state, cadaster_organisation, data_owner_cadastral_surveying,
                 transfer_from_source_cadastral_surveying, datasources):
        """
        The record for handling the address entity inside the application.

        Args:
            cadaster_state (datetime.datetime): Actuality of the oereb cadaster.
            cadaster_organisation (pyramid_oereb.lib.records.office.OfficeRecord): The information about the
                organisation which provides this cadaster.
            data_owner_cadastral_surveying (pyramid_oereb.lib.records.office.OfficeRecord): The information
                about the office which povides the surveying data for this extract.
            transfer_from_source_cadastral_surveying (datetime.datetime): The actuality of the surveying data
                used for this extract.
            datasources (list of pyramid_oereb.lib.records.embeddable.DatasourceRecord): All the datasource
                information on the extract.
        """

        # Filling out the 'pdf' attribute with pdf content is currently not supported by pyramid_oereb
        # More details in PR https://github.com/openoereb/pyramid_oereb/pull/601
        self.cadaster_state = cadaster_state
        self.cadaster_organisation = cadaster_organisation
        self.data_owner_cadastral_surveying = data_owner_cadastral_surveying
        self.transfer_from_source_cadastral_surveying = transfer_from_source_cadastral_surveying
        self.datasources = datasources


class DatasourceRecord(object):

    def __init__(self, theme, date, owner):
        """
        The record for handling the datasource entity for the embeddable flavour.

        Args:
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The topic of the datasource.
            date (datetime.datetime): Actuality of the topic.
            owner (pyramid_oereb.lib.records.office.OfficeRecord): The information about the organisation
                which is responsible for the topic.
        """
        self.theme = theme
        self.date = date
        self.owner = owner
