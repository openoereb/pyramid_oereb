# -*- coding: utf-8 -*-
"""
Regarding to the main documentation you find here all the stuff which is related to the records. You can
imagine these record things as the in-application-currency. They are achieved and structured in the
:ref:`base-sources`. They are gathered by the :ref:`readers`. And they are combined, sorted, dismissed and
reorganized by the processor.

.. note:: This layer is not meant to be adapted in normal.
"""


class BaseLookUpRecord(object):
    """
    Translation of codes delivered by fed in the
    https://models.geo.admin.ch/V_D/OeREB/OeREBKRM_V2_0_Texte_20210714.xml

    The specification wants the extract codes translated to english, here we have the key as
    the value defined in the xml and the value is the corresponding translation.
    """
    lookup = {}

    def __init__(self, code):
        if code not in self.lookup.keys():
            raise AttributeError('wrong code for law status was deliverd. Only {0} are'
                                 ' allowed. Value was {1}'.format(self.lookup.keys(), code))
        self.code = code

    def get_extract_code(self):
        return self.lookup[self.code]
