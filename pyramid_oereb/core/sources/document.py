# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.documents import DocumentRecord


class DocumentBaseSource(Base):
    """
    Base class for document sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.documents.DocumentRecord): List of document records.
    """
    _record_class_ = DocumentRecord

    def read(self, office_records):
        """
        Every document source has to implement a read method. This method must accept no parameters. Because
        it should deliver all items available.
        If you want adapt to your own source for documents, this is the point where to hook in.

        Args:
            office_records (pyramid_oereb.views.webservice.Parameter): The office records of the exact
                request.
        """
        pass  # pragma: no cover
