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

setup(
    name='pyramid_oereb',
    version='1.5.1',
    description='pyramid_oereb, extension for pyramid web frame work to provide '
            'a basic server part for the oereb project',
    long_description='{readme}\n\n{changes}'.format(readme=README, changes=CHANGES),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    license='BSD 2',
    author='Clemens Rudert',
    author_email='clemens.rudert@bl.ch',
    url='https://github.com/openoereb/pyramid_oereb',
    keywords='pyramid oereb',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'recommend': recommend,
        'no-version': requires,
    },
    entry_points={
        'paste.app_factory': [
            'main = pyramid_oereb:main'
        ],
        'console_scripts': [
            'create_standard_model = pyramid_oereb.standard.create_standard_models:create_standard_model',
            'create_oereblex_model = pyramid_oereb.contrib.scripts:create_oereblex_model',
            'create_standard_tables = pyramid_oereb.standard.create_tables:create_standard_tables',
            'create_theme_tables = pyramid_oereb.standard.create_tables:create_theme_tables',
            'create_standard_yaml = pyramid_oereb.standard.create_yaml:create_standard_yaml',
            'drop_standard_tables = pyramid_oereb.standard.drop_tables:drop_standard_tables',
            'create_legend_entries = pyramid_oereb.standard.load_legend_entries:run',
            'import_federal_topic = pyramid_oereb.standard.import_federal_topic:run'
        ]
    }
)
