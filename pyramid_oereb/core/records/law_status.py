# -*- coding: utf-8 -*-


class LawStatusRecord(object):
    """
    Law status record.
    """

    def __init__(self, code, title):
        """
        Create a new law status record.

        Args:
            code (str or unicode): The code of the law status. It must be "inKraft" or
            "AenderungMitVorwirkung" or "AenderungOhneVorwirkung" every other value will
            raise an error.
        title (dict of unicode): The multilingual law status description.
        """
        self.code = code
        self.title = title
