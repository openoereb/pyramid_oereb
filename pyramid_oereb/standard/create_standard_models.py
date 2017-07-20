# -*- coding: utf-8 -*-
import optparse
from pyramid_oereb.standard import _create_standard_configuration_models_py_


def create_standard_model():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create a python file which contais all sqlalchemy models in to hold oereb '
                    'specification like data'
    )
    parser.add_option(
        '-c', '--code',
        dest='code',
        metavar='OEREB NAME',
        type='string',
        help='The code/name for the oereb theme/topic/whatever. It must be camel case like: '
             'ForestPerimeters, ForestDistanceLines, NoiseSensitivityLevels,...'
    )
    parser.add_option(
        '-g', '--geometry_type',
        dest='geometry_type',
        metavar='GEOMETRYTYPE',
        type='string',
        help='The geometry type for this theme/topic/whatever. Possible values are:'
             'POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, MULTIPOLYGON, GEOMETRYCOLLECTION'
    )
    parser.add_option(
        '-p', '--target_path',
        dest='target_path',
        metavar='TARGET',
        type='string',
        help='The absolute path where the result will be stored.'
    )
    parser.add_option(
        '-s', '--schema',
        dest='schema',
        metavar='SCHEMA',
        type='string',
        help='The schema name. If not specified, it will be derived from the code.'
    )
    options, args = parser.parse_args()
    if not options.code:
        parser.error('No oereb code set.')
    if not options.geometry_type:
        parser.error('No geometry_type set.')
    if not options.target_path:
        parser.error('No target_path set.')
    _create_standard_configuration_models_py_(options.code, options.geometry_type, options.target_path,
                                              options.schema)
