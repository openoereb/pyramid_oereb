# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.view_service import LegendEntryRecord


class LegendBaseSource(Base):
    _record_class_ = LegendEntryRecord
