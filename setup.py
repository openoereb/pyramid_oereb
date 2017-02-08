# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

__author__ = 'Clemens Rudert'
__create_date__ = '01.02.2017'

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov'
]

requires = [
    'pyramid',
    'SQLAlchemy',
    'shapely',
    'dicttoxml',
    'geoalchemy2',
    'pyramid-georest',
    'transaction',
    'waitress',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'PyYAML',
    'psycopg2',
    'simplejson'
]

setup(
    name='pyramid_oereb',
    version='0.0.1',
    description='pyramid_oereb, extension for pyramid web frame work to provide '
            'a basic server part for the oereb project',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    license='GNU General Public License',
    author='Clemens Rudert',
    author_email='clemens.rudert@bl.ch',
    url='https://github.com/camptocamp/pyramid_oereb',
    keywords='pyramid oereb',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = pyramid_oereb:main

    """,
)
