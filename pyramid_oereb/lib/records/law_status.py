# -*- coding: utf-8 -*-


class LawStatusRecord(object):
    """
    Law status record.
    """

    def __init__(self, code, text):
        """
        Create a new law status record.

        Args:
            code (str or unicode): The code of the law status. It must be "inKraft" or
            "AenderungMitVorwirkung" or "AenderungOhneVorwirkung" every other value will
            raise an error.
        text (dict of unicode): The multilingual law status description.
        """

        if code != u'inKraft' and code != u'AenderungMitVorwirkung' and code != u'AenderungOhneVorwirkung':
            raise AttributeError('wrong code for law status was deliverd. Only "inKraft" or '
                                 '"AenderungMitVorwirkung" or "AenderungOhneVorwirkung" are'
                                 ' allowed. Value was {0}'.format(code))

        self.code = code
        self.text = text
