# -*- coding: utf-8 -*-

from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.records.address import AddressRecord


class AddressBaseSource(Base):
    _record_class_ = AddressRecord

    def read(self, street_name, zip_code, street_number):
        pass
