# -*- coding: utf-8 -*-
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.records.document_types import DocumentTypeRecord


class DocumentTypesBaseSource(Base):
    """
    Base class for document type values source.

    Attributes:
        records (list of pyramid_oereb.lib.records.document_types.DocumentTypeRecord): List of document
        type records.
    """
    _record_class_ = DocumentTypeRecord

    def read(self):
        """
        Every document type source has to implement a read method. This method must accept no parameters.
        Because it should deliver all items available.
        If you want adapt to your own source for document type labels, this is the point where to hook in.
        """
        pass  # pragma: no cover
