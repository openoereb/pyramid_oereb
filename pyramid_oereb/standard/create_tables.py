# -*- coding: utf-8 -*-
import argparse
from pyramid_oereb.standard import create_tables

__author__ = 'Clemens Rudert'
__create_date__ = '15.03.17'

parser = argparse.ArgumentParser(description='Create all content for the standard database')
parser.add_argument(
    '-c',
    '--configuration',
    help='The absolute path to the configuration yaml file (standard is: pyramid_oereb.yml).',
    required=True
)
parser.add_argument(
    '-s',
    '--section',
    help='The section which contains configruation (standard is: pyramid_oereb).',
    required=False
)
args = parser.parse_args()

section = 'pyramid_oereb'
configuration = args.configuration
if args.section:
    section = args.section
create_tables(configuration_yaml_path=configuration, section=section)
