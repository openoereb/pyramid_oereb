# -*- coding: utf-8 -*-
import logging.config
import optparse

from pyramid_oereb.standard.xtf_import import FederalTopic


# logging.basicConfig(level=logging.INFO)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'import_federal_topic': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
})


def run():

    parser = optparse.OptionParser(
        usage='usage: %prog [options] [file1.xml file2.xtf ...]',
        description='Import tool for federal OEREB topics. If no files are specified, the data will be '
                    'downloaded from the configured URL.'
    )
    parser.add_option(
        '-c', '--config',
        dest='config',
        metavar='YAML',
        type='string',
        help='The path to the configuration yaml file.'
    )
    parser.add_option(
        '-s', '--section',
        dest='section',
        metavar='SECTION',
        type='string',
        default='pyramid_oereb',
        help='The section which contains configuration (default is: pyramid_oereb).'
    )
    parser.add_option(
        '-t', '--topic',
        dest='topic_code',
        metavar='TOPIC_CODE',
        type='string',
        help='The topic code; has to be available in configuration!'
    )
    parser.add_option(
        '-f', '--force',
        dest='force',
        action='store_true',
        default=False,
        help='Skip comparing the checksums and force import.'
    )
    parser.add_option(
        '-S', '--srid',
        dest='srid',
        metavar='SRID',
        type='int',
        help='Overwrite SRID set in configuration file.'
    )
    parser.add_option(
        '-a', '--arc-max-diff',
        dest='arc_max_diff',
        metavar='MAX_DIFF',
        type='float',
        default=0.001,
        help='The maximum difference for stroked arcs (default is: 0.001).'
    )
    parser.add_option(
        '-A', '--arc-precision',
        dest='arc_precision',
        metavar='PRECISION',
        type='int',
        default=3,
        help='The decimal precision of generated arc coordinates (default is: 3).'
    )
    parser.add_option(
        '-d', '--temp-dir',
        dest='tmp_dir',
        metavar='TEMP_DIR',
        type='string',
        default='.',
        help='The temporary working directory. (default is ".")'
    )
    parser.add_option(
        '--c2ctemplate-style',
        dest='c2ctemplate_style',
        action='store_true',
        default=False,
        help='Is the yaml file using a c2ctemplate style (starting with vars)'
    )

    options, args = parser.parse_args()
    if not options.config:
        parser.error('No configuration file set.')
    if not options.topic_code:
        parser.error('No topic code defined.')

    download = not (len(args) > 0)

    loader = FederalTopic(
        options.config,
        options.topic_code,
        section=options.section,
        c2ctemplate_style=options.c2ctemplate_style,
        arc_max_diff=options.arc_max_diff,
        arc_precision=options.arc_precision,
        tmp_dir=options.tmp_dir,
        srid=options.srid
    )

    if download:
        loader.download_data()
        loader.unzip_data()
        loader.read_checksum()
        files = loader.collect_files()
    else:
        files = args

    loader.load(files, force=options.force)

    if download:
        loader.cleanup_files()
