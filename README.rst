===============================
``pyramid_oereb`` (ÖREB-Server)
===============================

|Build Status| |Requirements Status|

``pyramid_oereb`` is an open-source implementation of the server side part for the swiss `"Cadastre of
Public-law Restrictions on landownership" (PLR-cadastre) <https://www.cadastre.ch/en/oereb.html>`__.

It is written in Python and designed as a plugin for the `Pyramid Web Framework
<http://docs.pylonsproject.org/projects/pyramid/en/latest/>`__. This allows ``pyramid_oereb`` to be
included in any Pyramid web application.

Please refer to the `documentation <https://openoereb.github.io/pyramid_oereb/>`__ for detailed
information and instructions for installation and configuration.

If you are interested in contributing or extending the project, take a look at the
`contribution page <https://openoereb.github.io/pyramid_oereb/doc/contrib/>`__.

.. |Build Status| image:: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml/badge.svg
   :target: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml
   :alt: Build Status

.. |Requirements Status| image:: https://requires.io/github/openoereb/pyramid_oereb/requirements.svg?branch=master
   :target: https://requires.io/github/openoereb/pyramid_oereb/requirements/?branch=master
   :alt: Requirements Status

Local testing (quick preview)
=============================

Run dev server
--------------

Following packages are required: ``python3-venv`` ``postgresql-client`` ``libpq-dev``

Clone project:

.. code-block:: bash

  git clone git@github.com:openoereb/pyramid_oereb.git
  cd pyramid_oereb

The information for the connection to the main database, the print service and the statistics functionality database has to be provided in a .env file (not committed, copy sample.env and edit it if necessary):

.. code-block:: bash

  cp sample.env .env

Run:

.. code-block:: bash

  make serve

JSON reduced extract is accessible at: http://localhost:6543/oereb/extract/reduced/json/CH113928077734.


**When running in to issues installing** ``libpq-dev`` **:**

.. code-block:: bash

  The following packages have unmet dependencies:
   libpq-dev : Depends: libpq5 (= 10.12-0ubuntu0.18.04.1) but 12.3-1.pgdg18.04+1 is to be installed


Try to install a specific version (adapt the version to your requirement):

.. code-block:: bash

  sudo apt install libpq5=10.12-0ubuntu0.18.04.1


Run tests
---------

To check your code, run `make checks`. It will run style checks and tests. It's also possible to
run sub-target independently:

- ``make checks-style`` to run only style-related checks (linting).
- ``make tests`` to run tests. Python 3.7 is used by default. But you can run tests with another version by
  running: ``PYTHON_TEST_VERSION=python3.x make tests``. You can also set this variable in the Makefile.

After running tests, the coverage is available in the folder ``coverage_report``.

Use Oereblex data model
-----------------------

To test the application with the Oereblex data model, adapt the configuration files ``pyramid_oereb_standard.yml.mako`` and ``docker/config.yml.tmpl``.
See this example with the theme forest_perimeters:

.. code-block:: yaml

  source:
    # Standard data model
    #class: pyramid_oereb.standard.sources.plr.DatabaseSource
    # Oereblex data model
    class: pyramid_oereb.contrib.sources.plr_oereblex.DatabaseOEREBlexSource
    params:
      db_connection: *main_db_connection
      # Standard data model
      #models: pyramid_oereb.standard.models.forest_perimeters
      # Oereblex data model
      models: pyramid_oereb.contrib.models.oereblex.forest_perimeters

The sample data is in ``sample_data/oereblex``. 

Run the application:

.. code-block:: bash

  USE_OEREBLEX=TRUE make serve


JSON reduced extract is accessible at: http://localhost:6544/oereb/extract/reduced/json/CH113928077734. This will do a call to the Oereblex service defined in the configuration file, and the success of the call will depend on the external service being available, and the geolink id being used in the sample data still existing on the external system.

It is possible to run this instance in parallel to the instance which uses the standard database. For this, one should create a second clone of the project.

If testing ``make serve`` with another theme than forest_perimeters, changes will be necessary in the directory ``sample_data/oereblex/plr119``: first remove the symbolic link corresponding to this theme, then create a directory and add JSON data files into it. In comparison to the data from the standard model, a new attribute ``geolink`` is required in ``public_law_restriction.json``, which should correspond to an existing geolink in the Oereblex server defined in the configuration (see ``sample_data/oereblex/plr119/forest_perimeters`` for example files).
