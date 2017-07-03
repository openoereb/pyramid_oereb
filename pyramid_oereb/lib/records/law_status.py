# -*- coding: utf-8 -*-

from pyramid_oereb.lib.config import Config


class LawStatusRecord(object):

    def __init__(self, code):
        """
        Law status record.

        Args:
            code (str or unicode): The code of the law status. It must be "inForce" or "runningModifications"
                every other value will raise an error.
        """
        if code != u'inForce' and code != u'runningModifications':
            raise AttributeError('wrong code for law status was deliverd. Only "inForce" or '
                                 '"runningModifications" are allowed. Value was {0}'.format(code))

        self.code = code
        self.text = Config.get_law_status_translations(code)
