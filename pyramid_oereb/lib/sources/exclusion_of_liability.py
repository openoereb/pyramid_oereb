# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord


class ExclusionOfLiabilityBaseSource(Base):
    _record_class_ = ExclusionOfLiabilityRecord

    def read(self):
        pass  # pragma: no cover
