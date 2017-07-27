# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.glossary import GlossaryRecord


class GlossaryBaseSource(Base):
    _record_class_ = GlossaryRecord

    def read(self):
        pass  # pragma: no cover
