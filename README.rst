===============================
``pyramid_oereb`` (ÖREB-Server)
===============================

Project description
===================

``pyramid_oereb`` is an open-source implementation of the server side part for the swiss `"Cadastre of
Public-law Restrictions on landownership" (PLR-cadastre) <https://www.cadastre.ch/en/oereb.html>`__.

It is written in Python and designed as a plugin for the `Pyramid Web Framework
<http://docs.pylonsproject.org/projects/pyramid/en/latest/>`__. This allows ``pyramid_oereb`` to be
included in any Pyramid web application.

Please refer to the `documentation <https://openoereb.github.io/pyramid_oereb/>`__ for detailed
information and instructions for installation and configuration.

If you are interested in contributing or extending the project, take a look at the
`contribution page <https://openoereb.github.io/pyramid_oereb/doc/contrib/>`__.


Starting the development server
===============================

1. ``docker build -t pyramid_oereb:dev .``
2. Build run the initial build depending on you OS:
  * Linux: ``docker run --rm -v $(pwd):/workspace -u $(id -u):$(id -g) pyramid_oereb:dev make clean-all build``
  * MAC: ``docker run --rm -v $(pwd):/workspace pyramid_oereb:dev make clean-all build``
  * Windows CMD: ``docker run --rm -v %cd%:/workspace pyramid_oereb:dev make clean-all build``
  * Windows Powershell: ``docker run --rm -v ${PWD}:/workspace pyramid_oereb:dev make clean-all build``
5. ``docker-compose build``
6. ``docker-compose up``

Running ``docker-compose up`` will start the DB (it will automatically import the test/dev data on startup) and start
a running instance of the pyramid_oereb DEV server connected to the DB. The project folder is mounted
to it. So changes take effect.


Running the tests
=================

To run the tests locally (unix machine, windows users should go with the docker way described below):

1. Start the dev database with ``docker-compose up -d oereb-db`` (with the default config, this uses the default Postgres port on your machine)
2. Run the tests with ``make tests``

To run one specfic test:

.. code-block:: bash

  PYTEST_OPTS="-k <name_of_the_test>" make tests

To run all tests in a specific file or directory (omit the subfolder ``tests`` in ``PYTEST_PATH``):

.. code-block:: bash

  PYTEST_PATH="<path_to_test>"  make tests

To run the tests locally but inside Docker:

1. ``docker-compose build``
2. ``docker-compose up -d``
3. change line 7 in tests/resources/test_config.yml from ``postgresql://postgres:postgres@localhost:5432/oereb_test_db`` to ``postgresql://postgres:postgres@oereb-db:5432/oereb_test_db``
4. ``docker-compose exec oereb-server make test-core``


Using MapFish-Print
===================

To be able to test the OEREB static extract (pdf), you need to run ``pyramid_oereb`` with ``docker-compose`` and to have a running instance of `pyramid_oereb_mfp <https://github.com/openoereb/pyramid_oereb_mfp>`__.
The Docker network ``print-network`` is also required and can be created with:

.. code-block:: bash

  docker network create print-network

The sample static extract should then be available at http://localhost:6543/oereb/extract/pdf?EGRID=CH113928077734


CI Status
=========

CI status on master branch:

.. image:: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml/badge.svg
   :alt: Master CI status
   :target: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml

Daily check status:

.. image:: https://github.com/openoereb/pyramid_oereb/actions/workflows/daily_check.yaml/badge.svg
   :alt: Daily check status
   :target: https://github.com/openoereb/pyramid_oereb/actions/workflows/daily_check.yaml

Code Quality Status:

.. image:: https://api.codacy.com/project/badge/Grade/cf50094a4e84434d837babf1106f9fcb
   :alt: Codacy Badge
   :target: https://app.codacy.com/gh/openoereb/pyramid_oereb?utm_source=github.com&utm_medium=referral&utm_content=openoereb/pyramid_oereb&utm_campaign=Badge_Grade_Settings

Requirement status:

.. image:: https://requires.io/github/openoereb/pyramid_oereb/requirements.svg?branch=master
   :target: https://requires.io/github/openoereb/pyramid_oereb/requirements/?branch=master
   :alt: Requirements Status
