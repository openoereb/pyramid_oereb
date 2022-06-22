# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(HERE, 'CHANGES.rst')) as f:
    CHANGES = f.read()
with open('requirements.txt') as f:
    re_ = a = re.compile(r'(.+)==')
    recommend = f.read().splitlines()
requires = [re_.match(r).group(1) for r in recommend]

with open('requirements-tests.txt') as f:
    re_ = a = re.compile(r'(.+)==')
    tests_require = f.read().splitlines()

setup(
    name='pyramid_oereb',
    version='2.1.0',
    description='pyramid_oereb, extension for pyramid web frame work to provide '
            'a basic server part for the oereb project',
    long_description='FIXME',
    # long_description='{readme}\n\n{changes}'.format(readme=README, changes=CHANGES),
    long_description_content_type='text/x-rst',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    license='BSD 2',
    author='François Voisard',
    author_email='francois.voisard@ne.ch',
    url='https://github.com/openoereb/pyramid_oereb',
    keywords='pyramid oereb',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'recommend': recommend,
        'no-version': requires,
        'testing': tests_require
    },
    entry_points={
        'paste.app_factory': [
            'main = pyramid_oereb:main'
        ],
        'console_scripts': [
            'create_standard_tables = pyramid_oereb.contrib.data_sources.create_tables:create_standard_tables',  # noqa: E501
            'create_example_yaml = dev.config.create_yaml:create_yaml',
            'create_theme_tables = pyramid_oereb.contrib.data_sources.create_tables:create_theme_tables',
            'create_legend_entries = pyramid_oereb.contrib.data_sources.standard.load_legend_entries:run',
            'create_stats_tables = pyramid_oereb.contrib.stats.scripts.create_stats_tables:create_stats_tables'  # noqa: E501
        ]
    }
)
