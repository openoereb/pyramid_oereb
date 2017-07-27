# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.municipality import MunicipalityRecord


class MunicipalityBaseSource(Base):
    _record_class_ = MunicipalityRecord

    def read(self):
        pass  # pragma: no cover
