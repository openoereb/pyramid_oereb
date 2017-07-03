# -*- coding: utf-8 -*-

from pyramid_oereb.lib.config import Config


class LawStatusRecord(object):

    def __init__(self, code):
        """
        Responsible office record.

        Args:
            code (str or unicode):  The official name of the authority (multilingual)
        """
        if code != u'inForce' and code != u'runningModifications':
            raise AttributeError('wrong code for law status was deliverd. Only "inForce" or '
                                 '"runningModifications" are allowed. Value was {0}'.format(code))

        self.code = code
        self.text = Config.get_law_status_translations(code)
