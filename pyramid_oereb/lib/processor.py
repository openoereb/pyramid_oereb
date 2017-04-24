# -*- coding: utf-8 -*-
from pyramid.renderers import render_to_response
import json


class Processor(object):

    def __init__(self, params):
        from pyramid_oereb import real_estate_reader, extract_reader
        # TODO: add more flexible call to provide access via different inputs, and make it single response
        # only
        self.params = params
        real_estate_records = real_estate_reader.read(egrid=params.get('egrid'))
        self.extract = extract_reader.read(real_estate_records[0])

    def to_response(self):
        response_format = self.params.get('format')
        if response_format == 'json':
            return render_to_response('json', self.extract.to_extract())
        else:
            return None
