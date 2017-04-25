# -*- coding: utf-8 -*-
import pytest
from pyramid_oereb.lib.processor import Processor


@pytest.mark.parametrize("param", [
    {'geometry': False, 'images': False, 'egrid': u'CH113928077734', 'flavour': u'embeddable',
     'format': u'json'}
])
def test_init(param):
    with pytest.raises(LookupError):
        Processor(param)
