# -*- coding: utf-8 -*-


class LawStatusRecord(object):
    """
    Law status record.

    Attributes:
        code (str or unicode): The code of the law status. It must be "inForce" or
            "changeWithPreEffect" or "changeWithoutPreEffect" every other value will
            raise an error.
        title (dict of unicode): The multilingual law status description.
    """

    def __init__(self, code, title):
        """
        Args:
            code (str or unicode): The code of the law status. It must be "inForce" or
                "changeWithPreEffect" or "changeWithoutPreEffect" every other value will
                raise an error.
            title (dict of unicode): The multilingual law status description.
        """
        self.code = code
        self.title = title

    def __str__(self):
        return '<{} -- code: {} title: {}>'.format(
            self.__class__.__name__, self.code, self.title)
