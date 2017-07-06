# -*- coding: utf-8 -*-

from pyramid_oereb.lib.config import Config


class LawStatusRecord(object):
    """
    Law status record.
    """

    def __init__(self, code, text):
        """
        Create a new law status record.

        Args:
            code (str or unicode): The code of the law status. It must be "inForce" or "runningModifications"
                every other value will raise an error.
            text (dict of unicode): The multilingual law status description.
        """
        if code != u'inForce' and code != u'runningModifications':
            raise AttributeError('wrong code for law status was deliverd. Only "inForce" or '
                                 '"runningModifications" are allowed. Value was {0}'.format(code))

        self.code = code
        self.text = text

    @classmethod
    def from_config(cls, code):
        """
        Create a new law status record using the translations specified in the configuration.

        Args:
            code (str or unicode): The code of the law status. It must be "inForce" or "runningModifications"
                every other value will raise an error.

        Returns:
            pyramid_oereb.lib.records.law_status.LawStatusRecord: The created law status record.
        """
        return LawStatusRecord(code, Config.get_law_status_translations(code))
