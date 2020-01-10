# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.glossary import GlossaryRecord


class GlossaryBaseSource(Base):
    """
    Base class for address sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.glossary.GlossaryRecord): List of glossary records.
    """
    _record_class_ = GlossaryRecord

    def read(self, params):
        """
        Every glossary source has to implement a read method. This method must accept no parameters. Because
        it should deliver all items available.
        If you want adapt to your own source for glossaries, this is the point where to hook in.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
        """
        pass  # pragma: no cover
