# -*- coding: utf-8 -*-
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.real_estate import RealEstateRecord


class RealEstateBaseSource(Base):
    _record_class_ = RealEstateRecord

    def read(self, nb_ident=None, number=None, egrid=None, geometry=None):
        pass
