# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.glossary import GlossaryRecord


class GlossaryBaseSource(Base):
    """
    Base class for address sources.
    """
    _record_class_ = GlossaryRecord

    def read(self):
        """
        Every glossary source has to implement a read method. This method must accept no parameters. Because
        it should deliver all items available.
        If you want adapt to your own source for glossaries, this is the point where to hook in.

        Returns:
            list of pyramid_oereb.core.records.glossary.GlossaryRecord: The list of glossary records.
        """
        return list()
