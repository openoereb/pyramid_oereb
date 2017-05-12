# -*- coding: utf-8 -*-
from mako.template import Template
from pyramid.path import DottedNameResolver

from pyramid_oereb import ConfigReader
from pyramid_oereb.lib.readers.exclusion_of_liability import ExclusionOfLiabilityReader
from pyramid_oereb.lib.readers.glossary import GlossaryReader
from pyramid_oereb.lib.processor import Processor
from pyramid_oereb.lib.readers.real_estate import RealEstateReader
from pyramid_oereb.lib.readers.municipality import MunicipalityReader
from pyramid_oereb.lib.readers.extract import ExtractReader
from pyramid_oereb.views.webservice import Parameter


class XMLRenderer(object):
    def __init__(self):
        config_reader = ConfigReader('/home/vvmruder/Projekte/PyCharm/pyramid_oereb/'
                                     'pyramid_oereb_standard.yml', 'pyramid_oereb')
        real_estate_config = config_reader.get_real_estate_config()
        municipality_config = config_reader.get_municipality_config()
        exclusion_of_liability_config = config_reader.get_exclusion_of_liability_config()
        glossary_config = config_reader.get_glossary_config()
        logos = config_reader.get_logo_config()
        app_schema_name = config_reader.get('app_schema').get('name')
        srid = config_reader.get('srid')
        point_types = config_reader.get('plr_limits').get('point_types')
        line_types = config_reader.get('plr_limits').get('line_types')
        polygon_types = config_reader.get('plr_limits').get('polygon_types')
        min_length = config_reader.get('plr_limits').get('min_length')
        min_area = config_reader.get('plr_limits').get('min_area')
        plr_cadastre_authority = config_reader.get_plr_cadastre_authority()

        real_estate_reader = RealEstateReader(
            real_estate_config.get('source').get('class'),
            **real_estate_config.get('source').get('params')
        )

        municipality_reader = MunicipalityReader(
            municipality_config.get('source').get('class'),
            **municipality_config.get('source').get('params')
        )

        plr_sources = []
        for plr in config_reader.get('plrs'):
            plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
            plr_sources.append(plr_source_class(**plr))

        extract_reader = ExtractReader(
            plr_sources,
            plr_cadastre_authority,
            logos
        )
        exclusion_of_liability_reader = ExclusionOfLiabilityReader(
            exclusion_of_liability_config.get('source').get('class'),
            **exclusion_of_liability_config.get('source').get('params')
        )

        glossary_reader = GlossaryReader(
            glossary_config.get('source').get('class'),
            **glossary_config.get('source').get('params')
        )
        processor = Processor(
            real_estate_reader=real_estate_reader,
            municipality_reader=municipality_reader,
            exclusion_of_liability_reader=exclusion_of_liability_reader,
            glossary_reader=glossary_reader,
            plr_sources=plr_sources,
            extract_reader=extract_reader,
            point_types=point_types,
            line_types=line_types,
            polygon_types=polygon_types,
            min_length=min_length,
            min_area=min_area
        )
        params = Parameter('embeddable', 'xml', True, True, egrid='CH113928077734')
        real_estate_reader = processor.real_estate_reader
        real_estate_records = real_estate_reader.read(egrid='CH113928077734')
        extract = processor.process(real_estate_records[0])
        template = Template(filename='/home/vvmruder/Projekte/PyCharm/pyramid_oereb/pyramid_oereb/lib'
                                     '/renderer/templates/xml/extract.xml',
                            input_encoding='utf-8',
                            output_encoding='utf-8'
                            )
        content = template.render(**{
            'extract': extract,
            'params': params
        })
        f = open('/home/vvmruder/Projekte/temp/extract.xml', 'w+')
        f.write(content)
        f.close()
